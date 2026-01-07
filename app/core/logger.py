import logging
from pathlib import Path
import os


_logger = None
MAX_LOG_BYTES = 2 * 1024 * 1024
MAX_LOG_LINES = 2000


def log_dir():
    base = os.environ.get("APPDATA")
    if not base:
        base = os.path.expanduser("~\\AppData\\Roaming")
    path = Path(base) / "GreenBoost" / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def log_path():
    return log_dir() / "greenboost.log"


def init_logger():
    global _logger
    if _logger:
        return _logger
    _trim_log()
    logger = logging.getLogger("greenboost")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(log_path(), encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    _logger = logger
    return logger


def _trim_log():
    path = log_path()
    if not path.exists():
        return
    try:
        if path.stat().st_size <= MAX_LOG_BYTES:
            return
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) > MAX_LOG_LINES:
            lines = lines[-MAX_LOG_LINES:]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except Exception:
        return


def get_logger():
    return init_logger()


def read_recent_logs(level=None, limit=500):
    path = log_path()
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    if level:
        token = f" | {level.upper()} | "
        lines = [l for l in lines if token in l]
    return lines[-limit:]
