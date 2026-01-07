import winreg


KEY = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
VALUE = "ClearPageFileAtShutdown"


def set_clear_pagefile_at_shutdown(enabled):
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, VALUE, 0, winreg.REG_DWORD, 1 if enabled else 0)


def get_clear_pagefile_at_shutdown():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, VALUE)
            return bool(val)
    except FileNotFoundError:
        return False
    except OSError:
        return False
