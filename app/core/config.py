import json
import os
from pathlib import Path


DEFAULT_CONFIG = {
    "ui": {
        "theme": "system",
        "start_in_tray": True,
        "notifications": True,
    },
    "metrics": {
        "temp_threshold_mb": 2048,
    },
    "clean": {
        "custom_selection": ["user_temp", "app_logs"],
    },
    "auto_clean": {
        "enabled": False,
        "interval_min": 15,
        "profile": "quick",
        "paused": False,
        "conditions": {
            "ram_gt_enabled": False,
            "ram_gt": 85,
            "temp_gt_enabled": False,
            "temp_gt_mb": 2048,
            "idle_gt_enabled": False,
            "idle_gt_min": 10,
        },
    },
    "autostart": {
        "enabled": False,
        "mode": "registry",
        "start_in_tray": True,
    },
    "system": {
        "clear_pagefile_at_shutdown": False,
    },
    "last_clean": {
        "time": "",
        "freed_mb": 0,
        "profile": "",
    },
}


def app_data_dir():
    base = os.environ.get("APPDATA")
    if not base:
        base = os.path.expanduser("~\\AppData\\Roaming")
    path = Path(base) / "GreenBoost"
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_path():
    return app_data_dir() / "config.json"


def _merge(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _merge(dst[k], v)
        else:
            dst[k] = v


def load_config():
    path = config_path()
    if not path.exists():
        save_config(DEFAULT_CONFIG)
        return json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    merged = json.loads(json.dumps(DEFAULT_CONFIG))
    if isinstance(data, dict):
        _merge(merged, data)
    return merged


def save_config(cfg):
    path = config_path()
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def ensure_interval(value, min_value=5, max_value=1440):
    try:
        iv = int(value)
    except Exception:
        return min_value
    if iv < min_value:
        return min_value
    if iv > max_value:
        return max_value
    return iv
