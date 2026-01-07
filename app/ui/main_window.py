import os
import winreg
import time
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QTimer, QObject, Signal, QThread
from app.core.config import load_config, save_config, ensure_interval
from app.core.metrics import TempSizeCache, get_metrics
from app.core.cleaner import clean
from app.core.profiles import PROFILE_QUICK, PROFILE_DEEP
from app.core.logger import get_logger, read_recent_logs, log_dir
from app.core.idle import get_idle_seconds
from app.core.resources import icon_path
from app.platform.windows import autostart as autostart_api
from app.platform.windows import taskscheduler as task_api
from app.platform.windows import pagefile as pagefile_api
from app.platform.windows.privileges import is_admin, restart_as_admin
from .dashboard import DashboardView
from .cleaning import CleaningView
from .scheduler_view import SchedulerView
from .autostart_view import AutostartView
from .logs_view import LogsView
from .settings_view import SettingsView


logger = get_logger()


def human_mb(value):
    try:
        return round(value / (1024 * 1024), 1)
    except Exception:
        return 0


class CleanerWorker(QObject):
    progress = Signal(int, str)
    finished = Signal(dict)

    def __init__(self, selection, admin):
        super().__init__()
        self.selection = selection
        self.admin = admin

    def run(self):
        total = max(1, len(self.selection))
        state = {"idx": 0}

        def on_progress(label, detail):
            state["idx"] += 1
            pct = int(state["idx"] / total * 100)
            text = label if not detail else f"{label}: {detail}"
            self.progress.emit(pct, text)

        result = clean(self.selection, self.admin, progress=on_progress)
        self.finished.emit(result)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GreenBoost")
        self.setMinimumSize(880, 560)
        app_icon = icon_path()
        self.setWindowIcon(QIcon(app_icon))

        self.config = load_config()
        self.temp_cache = TempSizeCache()
        self.last_metrics = {}
        self.cleaning_busy = False
        self._current_profile = "quick"
        self._last_selection = []
        self._allow_close = False
        self._admin = is_admin()

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.nav = QWidget()
        self.nav.setObjectName("nav")
        self.nav.setFixedWidth(190)
        nav_layout = QVBoxLayout(self.nav)
        nav_layout.setContentsMargins(16, 16, 16, 16)
        nav_layout.setSpacing(8)

        self.app_label = QLabel("GreenBoost")
        self.app_label.setObjectName("title")
        nav_layout.addWidget(self.app_label)

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_cleaning = QPushButton("Cleaning")
        self.btn_scheduler = QPushButton("Scheduler")
        self.btn_autostart = QPushButton("Autostart")
        self.btn_logs = QPushButton("Logs")
        self.btn_settings = QPushButton("Settings")
        for b in [self.btn_dashboard, self.btn_cleaning, self.btn_scheduler, self.btn_autostart, self.btn_logs, self.btn_settings]:
            b.setProperty("nav", "true")
            nav_layout.addWidget(b)
        nav_layout.addStretch(1)
        layout.addWidget(self.nav, 0)

        self.stack = QStackedWidget()
        self.dashboard = DashboardView()
        self.cleaning = CleaningView()
        self.scheduler = SchedulerView()
        self.autostart = AutostartView()
        self.logs = LogsView()
        self.settings = SettingsView()
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.cleaning)
        self.stack.addWidget(self.scheduler)
        self.stack.addWidget(self.autostart)
        self.stack.addWidget(self.logs)
        self.stack.addWidget(self.settings)
        layout.addWidget(self.stack, 1)

        self.setCentralWidget(central)

        self.dashboard.quick_clean.connect(self.run_quick)
        self.dashboard.custom_clean.connect(self.open_custom)
        self.dashboard.show_formula.connect(self.show_formula)
        self.cleaning.start_clean.connect(self.run_custom)
        self.cleaning.deep_clean.connect(self.run_deep)
        self.scheduler.changed.connect(self.on_scheduler_changed)
        self.autostart.changed.connect(self.on_autostart_changed)
        self.autostart.restart_admin.connect(self.on_restart_admin)
        self.logs.refresh_requested.connect(self.refresh_logs)
        self.logs.open_folder.connect(self.open_logs_folder)
        self.settings.changed.connect(self.on_settings_changed)
        self.settings.about_requested.connect(self.show_about)

        self.nav_buttons = [
            (self.btn_dashboard, self.dashboard),
            (self.btn_cleaning, self.cleaning),
            (self.btn_scheduler, self.scheduler),
            (self.btn_autostart, self.autostart),
            (self.btn_logs, self.logs),
            (self.btn_settings, self.settings),
        ]
        for btn, view in self.nav_buttons:
            btn.clicked.connect(lambda _=None, v=view, b=btn: self.switch_view(v, b))

        self.tray = QSystemTrayIcon(QIcon(app_icon), self)
        menu = QMenu()
        self.tray_open = menu.addAction("Open")
        self.tray_quick = menu.addAction("Quick Clean")
        self.tray_pause = menu.addAction("Pause auto-clean")
        self.tray_settings = menu.addAction("Settings")
        self.tray_logs = menu.addAction("Show logs")
        menu.addSeparator()
        self.tray_exit = menu.addAction("Exit")
        self.tray.setContextMenu(menu)
        self.tray.show()

        self.tray_open.triggered.connect(self.show_window)
        self.tray_quick.triggered.connect(self.run_quick)
        self.tray_pause.triggered.connect(self.toggle_pause)
        self.tray_settings.triggered.connect(self.open_settings)
        self.tray_logs.triggered.connect(self.open_logs)
        self.tray_exit.triggered.connect(self.exit_app)
        self.tray.activated.connect(self.on_tray_activated)

        self.metrics_timer = QTimer(self)
        self.metrics_timer.timeout.connect(self.update_metrics)
        self.metrics_timer.start(2000)

        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self.auto_clean_tick)

        self.apply_config_to_ui()
        self.update_metrics()
        self.update_autoclean_timer()
        self.refresh_logs()
        self.set_active(self.btn_dashboard)

    def apply_config_to_ui(self):
        self.cleaning.set_selection(self.config["clean"].get("custom_selection", []))
        self.scheduler.set_state(self.config.get("auto_clean", {}))
        self.autostart.set_state({
            "enabled": self.config["autostart"].get("enabled", False),
            "mode": self.config["autostart"].get("mode", "registry"),
            "start_in_tray": self.config["autostart"].get("start_in_tray", True),
            "clear_pagefile_at_shutdown": self.config["system"].get("clear_pagefile_at_shutdown", False),
        })
        self.autostart.set_admin(self._admin)
        self.settings.set_state({
            "theme": self.config["ui"].get("theme", "system"),
            "temp_threshold_mb": self.config["metrics"].get("temp_threshold_mb", 2048),
            "notifications": self.config["ui"].get("notifications", True),
            "start_in_tray": self.config["ui"].get("start_in_tray", False),
        })
        self.dashboard.update_last_clean(
            self.config["last_clean"].get("time", ""),
            self.config["last_clean"].get("freed_mb", 0),
            self.config["last_clean"].get("profile", ""),
        )

    def open_custom(self, *_):
        self.stack.setCurrentWidget(self.cleaning)
        self.set_active(self.btn_cleaning)

    def switch_view(self, widget, button):
        self.stack.setCurrentWidget(widget)
        self.set_active(button)

    def set_active(self, active_button):
        for btn, _ in self.nav_buttons:
            btn.setProperty("active", btn is active_button)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

    def open_settings(self, *_):
        self.show_window()
        self.stack.setCurrentWidget(self.settings)
        self.set_active(self.btn_settings)

    def open_logs(self, *_):
        self.show_window()
        self.stack.setCurrentWidget(self.logs)
        self.set_active(self.btn_logs)

    def show_formula(self):
        msg = (
            "Index = clamp(0.45*RAM% + 0.25*Pagefile% + 0.20*DiskC% + 0.10*TempScore%, 0..100)\n"
            "TempScore% = clamp(TempSizeMB / TempThresholdMB * 100, 0..100)"
        )
        QMessageBox.information(self, "How the index is calculated", msg)

    def show_about(self):
        msg = (
            "GreenBoost is a lightweight system cleaning and monitoring utility."
        )
        QMessageBox.information(self, "About", msg)

    def update_metrics(self):
        threshold = self.config["metrics"].get("temp_threshold_mb", 2048)
        self.last_metrics = get_metrics(self.temp_cache, threshold)
        self.dashboard.update_metrics(self.last_metrics)
        ram_c = round(0.45 * self.last_metrics.get("ram", 0), 1)
        page_c = round(0.25 * self.last_metrics.get("pagefile", 0), 1)
        disk_c = round(0.20 * self.last_metrics.get("disk", 0), 1)
        temp_c = round(0.10 * self.last_metrics.get("temp_score", 0), 1)
        self.dashboard.update_breakdown(ram_c, page_c, disk_c, temp_c)
        tooltip = f"RAM: {self.last_metrics.get('ram', 0)}% | Disk C: {self.last_metrics.get('disk', 0)}% | Index: {self.last_metrics.get('index', 0)}%"
        self.tray.setToolTip(tooltip)

    def run_quick(self, *_):
        self.start_clean(PROFILE_QUICK, "quick", show_ui=False)

    def run_custom(self, selection):
        if not selection:
            self.notify("Select at least one category")
            return
        self.config["clean"]["custom_selection"] = selection
        save_config(self.config)
        self.start_clean(selection, "custom", show_ui=True)

    def run_deep(self, *_):
        text = "Deep clean may require administrator privileges and can take longer. Continue?"
        reply = QMessageBox.question(self, "Deep Clean", text, QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        self.start_clean(PROFILE_DEEP, "deep", show_ui=True)

    def start_clean(self, selection, profile_name, show_ui=False):
        if self.cleaning_busy:
            return
        self.cleaning_busy = True
        self._last_selection = selection
        self._current_profile = profile_name
        self.cleaning.reset_progress()
        self.dashboard.set_cleaning(True)
        if show_ui:
            self.stack.setCurrentWidget(self.cleaning)
            self.set_active(self.btn_cleaning)
        logger.info(f"Cleaning: profile={profile_name} categories={selection}")

        self.worker = CleanerWorker(selection, self._admin)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_clean_progress)
        self.worker.finished.connect(self.on_clean_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_clean_progress(self, pct, text):
        self.cleaning.set_progress(pct, text)

    def on_clean_finished(self, result):
        self.cleaning_busy = False
        self.dashboard.set_cleaning(False)
        profile_name = getattr(self, "_current_profile", "quick")
        freed_mb = human_mb(result.get("total_freed", 0))
        skipped = result.get("total_skipped", 0)
        msg = f"Cleaning finished: deleted {result.get('total_deleted', 0)} files, freed {freed_mb} MB, skipped {skipped}"
        details = []
        for key, res in result.get("by_category", {}).items():
            details.append(f"{key}: deleted={res.get('deleted_files',0)} freed={human_mb(res.get('freed_bytes',0))}MB skipped={res.get('skipped',0)} errors={res.get('errors',0)}")
        logger.info(f"Cleaning: profile={profile_name} | {msg} | {'; '.join(details)}")
        if not self._admin and result.get("by_category", {}).get("system_temp", {}).get("errors", 0) > 0:
            logger.warning("Windows Temp: insufficient privileges for full cleanup")
        self.config["last_clean"] = {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "freed_mb": freed_mb,
            "profile": profile_name,
        }
        save_config(self.config)
        self.dashboard.update_last_clean(self.config["last_clean"]["time"], freed_mb, profile_name)
        self.notify(f"Cleaning finished: freed {freed_mb} MB")
        if not self._admin and "system_temp" in getattr(self, "_last_selection", []) and result.get("by_category", {}).get("system_temp", {}).get("errors", 0) > 0:
            self.notify("Windows Temp cleanup failed — admin required")

    def on_scheduler_changed(self):
        state = self.scheduler.get_state()
        self.config["auto_clean"].update(state)
        self.config["auto_clean"]["interval_min"] = ensure_interval(self.config["auto_clean"].get("interval_min", 15))
        save_config(self.config)
        self.update_autoclean_timer()
        auto = self.config.get("auto_clean", {})
        if auto.get("enabled", False) and not auto.get("paused", False):
            self.auto_clean_tick()

    def update_autoclean_timer(self):
        auto = self.config.get("auto_clean", {})
        paused = auto.get("paused", False)
        enabled = auto.get("enabled", False)
        if enabled and not paused:
            interval = ensure_interval(auto.get("interval_min", 15))
            self.auto_timer.start(interval * 60 * 1000)
            self.tray_pause.setText("Pause auto-clean")
        else:
            self.auto_timer.stop()
            self.tray_pause.setText("Resume auto-clean")

    def auto_clean_tick(self):
        auto = self.config.get("auto_clean", {})
        if not auto.get("enabled", False):
            return
        if auto.get("paused", False):
            return
        cond = auto.get("conditions", {})
        if cond.get("ram_gt_enabled") and self.last_metrics.get("ram", 0) <= cond.get("ram_gt", 0):
            return
        if cond.get("temp_gt_enabled") and self.last_metrics.get("temp_mb", 0) <= cond.get("temp_gt_mb", 0):
            return
        if cond.get("idle_gt_enabled"):
            idle = get_idle_seconds()
            if idle < cond.get("idle_gt_min", 0) * 60:
                return
        profile = auto.get("profile", "quick")
        if profile == "custom":
            selection = self.config["clean"].get("custom_selection", [])
        else:
            selection = PROFILE_QUICK
        if not selection:
            return
        self.start_clean(selection, profile)

    def toggle_pause(self, *_):
        self.config["auto_clean"]["paused"] = not self.config["auto_clean"].get("paused", False)
        save_config(self.config)
        self.update_autoclean_timer()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show_window()

    def on_settings_changed(self):
        state = self.settings.get_state()
        self.config["ui"]["theme"] = state["theme"]
        self.config["ui"]["notifications"] = state["notifications"]
        self.config["ui"]["start_in_tray"] = state["start_in_tray"]
        self.config["metrics"]["temp_threshold_mb"] = state["temp_threshold_mb"]
        save_config(self.config)
        self.apply_theme()

    def on_autostart_changed(self):
        state = self.autostart.get_state()
        self.config["autostart"]["enabled"] = state["autostart"]
        self.config["autostart"]["mode"] = state["mode"]
        self.config["autostart"]["start_in_tray"] = state["start_in_tray"]
        save_config(self.config)

        ok = True
        if state["autostart"]:
            if state["mode"] == "registry":
                try:
                    autostart_api.set_autostart(True, state["start_in_tray"])
                except Exception as e:
                    ok = False
                    self.notify(f"Autostart failed: {e}")
            else:
                if not task_api.create_task(state["start_in_tray"]):
                    ok = False
                    self.notify("Autostart failed: Task Scheduler entry not created")
        else:
            if state["mode"] == "registry":
                try:
                    autostart_api.set_autostart(False, state["start_in_tray"])
                except Exception:
                    ok = False
            else:
                task_api.delete_task()

        if not ok:
            self.config["autostart"]["enabled"] = False
            save_config(self.config)
            self.autostart.set_state({
                "enabled": False,
                "mode": self.config["autostart"].get("mode", "registry"),
                "start_in_tray": self.config["autostart"].get("start_in_tray", True),
                "clear_pagefile_at_shutdown": self.config["system"].get("clear_pagefile_at_shutdown", False),
            })

        if state["clear_pagefile"] != self.config["system"].get("clear_pagefile_at_shutdown", False):
            if not self._admin:
                self.notify("Pagefile change requires administrator privileges")
                self.autostart.set_state({
                    "enabled": self.config["autostart"].get("enabled", False),
                    "mode": self.config["autostart"].get("mode", "registry"),
                    "start_in_tray": self.config["autostart"].get("start_in_tray", True),
                    "clear_pagefile_at_shutdown": self.config["system"].get("clear_pagefile_at_shutdown", False),
                })
                return
            try:
                pagefile_api.set_clear_pagefile_at_shutdown(state["clear_pagefile"])
                self.config["system"]["clear_pagefile_at_shutdown"] = state["clear_pagefile"]
                save_config(self.config)
                logger.info(f"ClearPageFileAtShutdown set to {state['clear_pagefile']}")
            except Exception as e:
                self.notify(f"Pagefile setting failed: {e}")

    def on_restart_admin(self):
        if restart_as_admin():
            self.exit_app()
        else:
            self.notify("Failed to restart with administrator privileges")

    def refresh_logs(self):
        mode = self.logs.filter.currentData()
        level = None
        if mode == "info":
            level = "INFO"
        elif mode == "warning":
            level = "WARNING"
        elif mode == "error":
            level = "ERROR"
        lines = read_recent_logs(level=level, limit=500)
        self.logs.set_logs(lines)

    def open_logs_folder(self):
        path = str(log_dir())
        try:
            os.startfile(path)
        except Exception:
            self.notify("Failed to open logs folder")

    def show_window(self, *_):
        self.show()
        self.raise_()
        self.activateWindow()
        self.metrics_timer.setInterval(2000)

    def exit_app(self, *_):
        self._allow_close = True
        self.tray.hide()
        self.close()

    def closeEvent(self, event):
        if self._allow_close:
            event.accept()
            return
        if self.config["ui"].get("start_in_tray", True):
            event.ignore()
            self.hide()
            self.metrics_timer.setInterval(8000)
            self.notify("App is still running in the background")
        else:
            event.accept()

    def notify(self, message):
        if self.config["ui"].get("notifications", True):
            self.tray.showMessage("GreenBoost", message)

    def apply_theme(self):
        theme = self.config["ui"].get("theme", "system")
        if theme == "system":
            theme = self.get_system_theme()
        from .styles import get_qss
        self.setStyleSheet(get_qss(theme))

    def get_system_theme(self):
        key = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
                val, _ = winreg.QueryValueEx(k, "AppsUseLightTheme")
                return "light" if val == 1 else "dark"
        except Exception:
            return "light"

    def toggle_hidden_start(self, start_hidden):
        if start_hidden:
            self.hide()
            self.metrics_timer.setInterval(8000)
        else:
            self.show_window()
