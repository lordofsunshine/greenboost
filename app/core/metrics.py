import os
import time
import threading
import psutil
from .logger import get_logger


logger = get_logger()


def clamp(value, low=0, high=100):
    if value < low:
        return low
    if value > high:
        return high
    return value


def _dir_size_bytes(path):
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            for name in files:
                fp = os.path.join(root, name)
                try:
                    total += os.path.getsize(fp)
                except Exception:
                    continue
    except Exception:
        return 0
    return total


class TempSizeCache:
    def __init__(self, interval_sec=10):
        self.interval_sec = interval_sec
        self._last_at = 0
        self._last_mb = 0
        self._running = False
        self._lock = threading.Lock()

    def get(self):
        now = time.time()
        if now - self._last_at < self.interval_sec:
            return self._last_mb
        if not self._running:
            self._running = True
            threading.Thread(target=self._refresh, daemon=True).start()
        return self._last_mb

    def _refresh(self):
        try:
            user_temp = os.environ.get("TEMP") or os.environ.get("TMP") or ""
            system_temp = "C:\\Windows\\Temp"
            size_bytes = 0
            if user_temp:
                size_bytes += _dir_size_bytes(user_temp)
            try:
                size_bytes += _dir_size_bytes(system_temp)
            except Exception:
                pass
            with self._lock:
                self._last_at = time.time()
                self._last_mb = int(size_bytes / (1024 * 1024))
        finally:
            with self._lock:
                self._running = False


def get_metrics(temp_cache, temp_threshold_mb):
    try:
        ram = psutil.virtual_memory().percent
    except Exception as e:
        logger.warning(f"RAM metric error: {e}")
        ram = 0
    try:
        pagefile = psutil.swap_memory().percent
    except Exception as e:
        logger.warning(f"Pagefile metric error: {e}")
        pagefile = 0
    try:
        disk = psutil.disk_usage("C:\\").percent
    except Exception as e:
        logger.warning(f"Disk metric error: {e}")
        disk = 0
    temp_size_mb = temp_cache.get() if temp_cache else 0
    try:
        temp_score = clamp((temp_size_mb / max(1, temp_threshold_mb)) * 100)
    except Exception:
        temp_score = 0
    index = clamp(0.45 * ram + 0.25 * pagefile + 0.20 * disk + 0.10 * temp_score)
    return {
        "ram": round(ram, 1),
        "pagefile": round(pagefile, 1),
        "disk": round(disk, 1),
        "temp_mb": temp_size_mb,
        "temp_score": round(temp_score, 1),
        "index": round(index, 1),
    }
