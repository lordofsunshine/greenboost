from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton, QGroupBox
from PySide6.QtCore import Signal, QSignalBlocker


class AutostartView(QWidget):
    changed = Signal()
    restart_admin = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(14)

        self.autostart = QCheckBox("Start with Windows")
        main.addWidget(self.autostart)

        row = QHBoxLayout()
        row.addWidget(QLabel("Autostart mode"))
        self.mode = QComboBox()
        self.mode.addItem("HKCU Run (no admin)", "registry")
        self.mode.addItem("Task Scheduler (elevated)", "task")
        row.addWidget(self.mode)
        row.addStretch(1)
        main.addLayout(row)

        self.mode_note = QLabel("registry — no admin; task — elevated start via Task Scheduler")
        self.mode_note.setWordWrap(True)
        main.addWidget(self.mode_note)

        self.start_tray = QCheckBox("Start in tray")
        main.addWidget(self.start_tray)

        sys_box = QGroupBox("System features")
        sys_layout = QVBoxLayout(sys_box)
        self.clear_pagefile = QCheckBox("Clear pagefile on shutdown")
        self.clear_note = QLabel("Pagefile clearing happens on Windows shutdown and may increase shutdown time.")
        self.clear_note.setWordWrap(True)
        sys_layout.addWidget(self.clear_pagefile)
        sys_layout.addWidget(self.clear_note)
        main.addWidget(sys_box)

        self.admin_btn = QPushButton("Restart as administrator")
        main.addWidget(self.admin_btn)

        self.autostart.stateChanged.connect(lambda _=None: self.changed.emit())
        self.mode.currentIndexChanged.connect(lambda _=None: self.changed.emit())
        self.start_tray.stateChanged.connect(lambda _=None: self.changed.emit())
        self.clear_pagefile.stateChanged.connect(lambda _=None: self.changed.emit())
        self.admin_btn.clicked.connect(self.restart_admin.emit)

    def get_state(self):
        mode = self.mode.currentData()
        return {
            "autostart": self.autostart.isChecked(),
            "mode": mode if mode else "registry",
            "start_in_tray": self.start_tray.isChecked(),
            "clear_pagefile": self.clear_pagefile.isChecked(),
        }

    def set_state(self, data):
        blockers = [
            QSignalBlocker(self.autostart),
            QSignalBlocker(self.mode),
            QSignalBlocker(self.start_tray),
            QSignalBlocker(self.clear_pagefile),
        ]
        self.autostart.setChecked(data.get("enabled", False))
        mode = data.get("mode", "registry")
        idx = self.mode.findData(mode)
        if idx >= 0:
            self.mode.setCurrentIndex(idx)
        else:
            self.mode.setCurrentIndex(0)
        self.start_tray.setChecked(data.get("start_in_tray", True))
        self.clear_pagefile.setChecked(data.get("clear_pagefile_at_shutdown", False))
        del blockers

    def set_admin(self, is_admin):
        if is_admin:
            self.admin_btn.setText("Running as administrator")
            self.admin_btn.setEnabled(False)
        else:
            self.admin_btn.setText("Restart as administrator")
            self.admin_btn.setEnabled(True)
