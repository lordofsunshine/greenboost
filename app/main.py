import sys
import argparse
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from app.core.config import load_config
from app.core.logger import get_logger
from app.core.metrics import TempSizeCache, get_metrics
from app.ui.main_window import MainWindow
from app.core.resources import icon_path


logger = get_logger()


def smoke_check():
    cfg = load_config()
    cache = TempSizeCache(interval_sec=1)
    metrics = get_metrics(cache, cfg["metrics"].get("temp_threshold_mb", 2048))
    logger.info(f"Smoke check metrics: {metrics}")


def _activate_existing():
    try:
        import win32con
        import win32gui
        hwnd = win32gui.FindWindow(None, "GreenBoost")
        if not hwnd:
            return False
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.BringWindowToTop(hwnd)
        win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception:
        return False


def _notify_already_running():
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, "GreenBoost is already running. Check the tray.", "GreenBoost", 0x40)
    except Exception:
        print("GreenBoost is already running. Check the tray.")


def ensure_single_instance():
    try:
        import win32event
        import win32api
        import winerror
        name = "Global\\GreenBoostSingleton"
        if not getattr(sys, "frozen", False):
            name = "Global\\GreenBoostSingletonDev"
        mutex = win32event.CreateMutex(None, False, name)
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            if not _activate_existing():
                _notify_already_running()
            return False
        global _GB_MUTEX
        _GB_MUTEX = mutex
        return True
    except Exception:
        return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tray", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    if args.smoke:
        smoke_check()
        return
    if not ensure_single_instance():
        return

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(icon_path()))

    window = MainWindow()
    window.apply_theme()

    if args.tray:
        window.toggle_hidden_start(True)
    else:
        window.show()

    app.exec()


if __name__ == "__main__":
    main()
