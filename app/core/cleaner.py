import os
import subprocess
import ctypes
from pathlib import Path
from .logger import get_logger, log_path, log_dir


logger = get_logger()


def _delete_dir_contents(path, on_file=None):
    deleted_files = 0
    freed_bytes = 0
    skipped = 0
    errors = 0
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            fp = os.path.join(root, name)
            try:
                size = os.path.getsize(fp)
            except Exception:
                size = 0
            try:
                os.remove(fp)
                deleted_files += 1
                freed_bytes += size
                if on_file:
                    on_file(fp)
            except Exception:
                skipped += 1
                errors += 1
        for d in dirs:
            dp = os.path.join(root, d)
            try:
                os.rmdir(dp)
            except Exception:
                continue
    return {
        "deleted_files": deleted_files,
        "freed_bytes": freed_bytes,
        "skipped": skipped,
        "errors": errors,
    }


def _clean_user_temp(progress):
    path = os.environ.get("TEMP") or os.environ.get("TMP")
    if not path or not os.path.isdir(path):
        return {"deleted_files": 0, "freed_bytes": 0, "skipped": 0, "errors": 1}
    progress("User Temp", path)
    return _delete_dir_contents(path)


def _clean_system_temp(progress):
    path = "C:\\Windows\\Temp"
    if not os.path.isdir(path):
        return {"deleted_files": 0, "freed_bytes": 0, "skipped": 0, "errors": 1}
    progress("Windows Temp", path)
    return _delete_dir_contents(path)


def _clean_recycle_bin(progress):
    progress("Recycle Bin", "")
    SHERB_NOCONFIRMATION = 0x00000001
    SHERB_NOPROGRESSUI = 0x00000002
    SHERB_NOSOUND = 0x00000004
    try:
        res = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND)
        if res != 0:
            return {"deleted_files": 0, "freed_bytes": 0, "skipped": 0, "errors": 1}
    except Exception:
        return {"deleted_files": 0, "freed_bytes": 0, "skipped": 0, "errors": 1}
    return {"deleted_files": 0, "freed_bytes": 0, "skipped": 0, "errors": 0}


def _clean_dns_cache(progress):
    progress("DNS cache", "")
    try:
        completed = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, shell=False)
        if completed.returncode != 0:
            return {"deleted_files": 0, "freed_bytes": 0, "skipped": 0, "errors": 1}
    except Exception:
        return {"deleted_files": 0, "freed_bytes": 0, "skipped": 0, "errors": 1}
    return {"deleted_files": 0, "freed_bytes": 0, "skipped": 0, "errors": 0}


def _clean_app_logs(progress):
    progress("GreenBoost logs", str(log_dir()))
    deleted_files = 0
    freed_bytes = 0
    skipped = 0
    errors = 0
    current = str(log_path())
    for p in Path(log_dir()).glob("*.log"):
        if str(p) == current:
            continue
        try:
            size = p.stat().st_size
        except Exception:
            size = 0
        try:
            p.unlink(missing_ok=True)
            deleted_files += 1
            freed_bytes += size
        except Exception:
            skipped += 1
            errors += 1
    return {
        "deleted_files": deleted_files,
        "freed_bytes": freed_bytes,
        "skipped": skipped,
        "errors": errors,
    }


def clean(selected, is_admin, progress=None):
    if progress is None:
        def progress(a, b):
            return None
    results = {}
    total_deleted = 0
    total_freed = 0
    total_skipped = 0
    total_errors = 0
    for key in selected:
        if key == "user_temp":
            res = _clean_user_temp(progress)
        elif key == "system_temp":
            res = _clean_system_temp(progress)
        elif key == "recycle_bin":
            res = _clean_recycle_bin(progress)
        elif key == "dns_cache":
            if not is_admin:
                logger.warning("DNS cache: administrator required")
                res = {"deleted_files": 0, "freed_bytes": 0, "skipped": 0, "errors": 1}
            else:
                res = _clean_dns_cache(progress)
        elif key == "app_logs":
            res = _clean_app_logs(progress)
        else:
            res = {"deleted_files": 0, "freed_bytes": 0, "skipped": 0, "errors": 1}
        results[key] = res
        total_deleted += res.get("deleted_files", 0)
        total_freed += res.get("freed_bytes", 0)
        total_skipped += res.get("skipped", 0)
        total_errors += res.get("errors", 0)
    return {
        "total_deleted": total_deleted,
        "total_freed": total_freed,
        "total_skipped": total_skipped,
        "total_errors": total_errors,
        "by_category": results,
    }
