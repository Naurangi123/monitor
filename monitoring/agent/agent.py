
import json, socket, sys, time
from datetime import datetime, timezone
from pathlib import Path
import psutil
import requests


DEFAULT_CONFIG = {
    "endpoint": "http://127.0.0.1:8000/api/ingest/",
    "api_key": "super-secret-agent-key",
    "hostname": None,
    "interval": 30  
}

def load_config():
    cfg = DEFAULT_CONFIG.copy()
    p = Path(__file__).with_name("config.json")
    if p.exists():
        try:
            file_cfg = json.loads(p.read_text())
            cfg.update(file_cfg)
        except Exception as e:
            print("Could not read config.json, using defaults:", e)
    return cfg


def collect_system_stats():
    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "used": psutil.virtual_memory().used,
            "percent": psutil.virtual_memory().percent,
        },
        "network": {
            "bytes_sent": psutil.net_io_counters().bytes_sent,
            "bytes_recv": psutil.net_io_counters().bytes_recv,
            "packets_sent": psutil.net_io_counters().packets_sent,
            "packets_recv": psutil.net_io_counters().packets_recv,
        },
    }

def collect_snapshot():
    procs = []
    for p in psutil.process_iter(attrs=["pid", "ppid", "name", "cmdline", "memory_info"]):
        try:
            info = p.info
            procs.append({
                "pid": info.get("pid"),
                "ppid": info.get("ppid"),
                "name": info.get("name") or "",
                "cmdline": " ".join(info.get("cmdline") or []),
                "cpu_percent": p.cpu_percent(interval=None),
                "memory_rss": getattr(info.get("memory_info"), "rss", None)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procs

def run_agent(cfg):
    endpoint = cfg["endpoint"].rstrip("/") + "/"
    api_key = cfg["api_key"]
    hostname = cfg["hostname"] or socket.gethostname()
    interval = cfg["interval"]

    headers = {"Content-Type": "application/json", "X-API-Key": api_key}

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
            "processes": collect_snapshot()
        }

        try:
            r = requests.post(endpoint, headers=headers, json=payload, timeout=15)
            r.raise_for_status()
            print("Ingest ok:", r.json())
        except requests.RequestException as e:
            print("Ingest failed:", e)

        # time.sleep(interval)

if __name__ == "__main__":
    cfg = load_config()
    run_agent(cfg)

