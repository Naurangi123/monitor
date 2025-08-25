import json, socket, sys, time
from datetime import datetime, timezone
from pathlib import Path
import psutil, requests

DEFAULT_CONFIG = {
    "endpoint": "http://127.0.0.1:8000/api/ingest/",
    "api_key": "super-secret-agent-key",
    "hostname": None,
    "interval": 60,
}

def load_config():
    cfg = DEFAULT_CONFIG.copy()
    p = Path(__file__).with_name("config.json")
    if p.exists():
        try:
            cfg.update(json.loads(p.read_text()))
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
            "percent": vm.percent
        },
        "network": {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv
        },
    }

def collect_snapshot():
    procs = []
    for proc in psutil.process_iter(attrs=["pid", "ppid", "name", "cmdline", "memory_info"]):
        try:
            info = proc.info
            nm = info.get("name") or f"pid-{info['pid']}"
            procs.append({
                "pid": info["pid"],
                "ppid": info["ppid"],
                "name": nm,
                "status": proc.status(),
                "cmdline": " ".join(info.get("cmdline") or []),
                "cpu_percent": proc.cpu_percent(interval=None),
                "memory_rss": getattr(info["memory_info"], "rss", None),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procs

def run_agent(cfg):
    endpoint = cfg["endpoint"].rstrip("/") + "/"
    headers = {"Content-Type": "application/json", "X-API-Key": cfg["api_key"]}
    hostname = cfg["hostname"] or socket.gethostname()
    interval = cfg.get("interval", 60)
    psutil.cpu_percent(interval=None)
    for p in psutil.process_iter():
        try: p.cpu_percent(interval=None)
        except: pass
    while True:
        payload = {
            "hostname": hostname,
            "snapshot_time": datetime.now(timezone.utc).isoformat(),
            "system": collect_system_stats(),
            "processes": collect_snapshot(),
        }
        try:
            r = requests.post(endpoint, headers=headers, json=payload, timeout=15)
            r.raise_for_status()
            print(f"[INFO] Ingest ok: {r.json()}")
        except requests.RequestException as e:
            print(f"[ERROR] Ingest failed: {e}", file=sys.stderr)
        time.sleep(interval)

if __name__ == "__main__":
    cfg = load_config()
    try:
        run_agent(cfg)
    except KeyboardInterrupt:
        print("\n[INFO] Agent stopped by user")
