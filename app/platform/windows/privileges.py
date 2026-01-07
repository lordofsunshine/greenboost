import ctypes
import sys


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def restart_as_admin():
    if is_admin():
        return True
    args = " ".join([f'"{a}"' for a in sys.argv[1:]])
    exe = sys.executable
    if getattr(sys, "frozen", False):
        params = args
    else:
        params = f"-m app.main {args}".strip()
    try:
        res = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)
        return res > 32
    except Exception:
        return False
