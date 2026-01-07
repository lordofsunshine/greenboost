from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox, QCheckBox, QPushButton
from PySide6.QtCore import Signal, QSignalBlocker


class SettingsView(QWidget):
    changed = Signal()
    about_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(14)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Theme"))
        self.theme = QComboBox()
        self.theme.addItem("System", "system")
        self.theme.addItem("Light", "light")
        self.theme.addItem("Dark", "dark")
        row1.addWidget(self.theme)
        row1.addStretch(1)
        main.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Temp threshold (MB)"))
        self.temp_threshold = QSpinBox()
        self.temp_threshold.setRange(256, 16384)
        row2.addWidget(self.temp_threshold)
        row2.addStretch(1)
        main.addLayout(row2)

        self.notifications = QCheckBox("Show notifications")
        main.addWidget(self.notifications)

        self.start_in_tray = QCheckBox("Keep running in tray when closed")
        main.addWidget(self.start_in_tray)

        self.about_btn = QPushButton("About")
        main.addWidget(self.about_btn)

        self.theme.currentIndexChanged.connect(lambda _=None: self.changed.emit())
        self.temp_threshold.valueChanged.connect(lambda _=None: self.changed.emit())
        self.notifications.stateChanged.connect(lambda _=None: self.changed.emit())
        self.start_in_tray.stateChanged.connect(lambda _=None: self.changed.emit())
        self.about_btn.clicked.connect(lambda _=None: self.about_requested.emit())

    def get_state(self):
        theme = self.theme.currentData()
        return {
            "theme": theme if theme else "system",
            "temp_threshold_mb": self.temp_threshold.value(),
            "notifications": self.notifications.isChecked(),
            "start_in_tray": self.start_in_tray.isChecked(),
        }

    def set_state(self, data):
        blockers = [
            QSignalBlocker(self.theme),
            QSignalBlocker(self.temp_threshold),
            QSignalBlocker(self.notifications),
            QSignalBlocker(self.start_in_tray),
        ]
        theme = data.get("theme", "system")
        idx = self.theme.findData(theme)
        if idx >= 0:
            self.theme.setCurrentIndex(idx)
        else:
            self.theme.setCurrentIndex(0)
        self.temp_threshold.setValue(int(data.get("temp_threshold_mb", 2048)))
        self.notifications.setChecked(data.get("notifications", True))
        self.start_in_tray.setChecked(data.get("start_in_tray", False))
        del blockers
