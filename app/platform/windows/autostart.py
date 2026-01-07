import sys
import winreg


RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "GreenBoost"


def _app_command(start_in_tray=False):
    exe = sys.executable
    args = []
    if not getattr(sys, "frozen", False):
        args += ["-m", "app.main"]
    if start_in_tray:
        args += ["--tray"]
    cmd = " ".join([f'"{exe}"'] + [f'"{a}"' for a in args])
    return cmd


def set_autostart(enabled, start_in_tray=False):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, _app_command(start_in_tray))
        else:
            try:
                winreg.DeleteValue(key, VALUE_NAME)
            except FileNotFoundError:
                pass


def is_autostart_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, VALUE_NAME)
            return True
    except FileNotFoundError:
        return False
    except OSError:
        return False
