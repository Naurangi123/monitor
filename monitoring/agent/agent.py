import json
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil
import requests


DEFAULT_CONFIG = {
    "endpoint": "http://127.0.0.1:8000/api/ingest/",
    "api_key": "super-secret-agent-key",
    "hostname": None,
    "interval": 60,  
}


def load_config():
    cfg = DEFAULT_CONFIG.copy()
    config_file = Path(__file__).with_name("config.json")

    if config_file.exists():
        try:
            with config_file.open("r", encoding="utf-8") as f:
                file_cfg = json.load(f)
                cfg.update(file_cfg)
        except Exception as e:
            print(f"[WARN] Could not parse config.json: {e}", file=sys.stderr)

    return cfg


def collect_system_stats():
    vm = psutil.virtual_memory()
    net = psutil.net_io_counters()

    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory": {
            "total": vm.total,
            "available": vm.available,
            "used": vm.used,
            "percent": vm.percent,
        },
        "network": {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        },
    }


def collect_snapshot():
    procs = []
    for proc in psutil.process_iter(attrs=["pid", "ppid", "name", "cmdline", "memory_info"]):
        try:
            info = proc.info
            procs.append({
                "pid": info["pid"],
                "ppid": info["ppid"],
                "name": info.get("name") or "",
                "cmdline": " ".join(info.get("cmdline") or []),
                "cpu_percent": proc.cpu_percent(interval=None),
                "memory_rss": getattr(info["memory_info"], "rss", None),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procs


def run_agent(cfg):
    endpoint = cfg["endpoint"].rstrip("/") + "/"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": cfg["api_key"],
    }

    hostname = cfg["hostname"] or socket.gethostname()
    interval = cfg.get("interval", 60)

    psutil.cpu_percent(interval=None)
    for p in psutil.process_iter():
        try:
            p.cpu_percent(interval=None)
        except Exception:
            pass

    while True:
        payload = {
            "hostname": hostname,
            "snapshot_time": datetime.now(timezone.utc).isoformat(),
            "system": collect_system_stats(),
            "processes": collect_snapshot(),
        }

        try:
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=15)
            resp.raise_for_status()
            print(f"[INFO] Ingest ok: {resp.json()}")
        except requests.RequestException as e:
            print(f"[ERROR] Ingest failed: {e}", file=sys.stderr)

        time.sleep(interval)


if __name__ == "__main__":
    config = load_config()
    try:
        run_agent(config)
    except KeyboardInterrupt:
        print("\n[INFO] Agent stopped by user")
