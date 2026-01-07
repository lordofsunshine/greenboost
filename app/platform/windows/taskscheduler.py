import subprocess
import sys


TASK_NAME = "GreenBoost"


def _app_command(start_in_tray=False):
    exe = sys.executable
    args = []
    if not getattr(sys, "frozen", False):
        args += ["-m", "app.main"]
    if start_in_tray:
        args += ["--tray"]
    return " ".join([f'"{exe}"'] + [f'"{a}"' for a in args])


def create_task(start_in_tray=False):
    cmd = _app_command(start_in_tray)
    args = [
        "schtasks",
        "/Create",
        "/F",
        "/SC",
        "ONLOGON",
        "/RL",
        "HIGHEST",
        "/TN",
        TASK_NAME,
        "/TR",
        cmd,
    ]
    res = subprocess.run(args, capture_output=True, text=True)
    return res.returncode == 0


def delete_task():
    res = subprocess.run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"], capture_output=True, text=True)
    return res.returncode == 0


def task_exists():
    res = subprocess.run(["schtasks", "/Query", "/TN", TASK_NAME], capture_output=True, text=True)
    return res.returncode == 0
