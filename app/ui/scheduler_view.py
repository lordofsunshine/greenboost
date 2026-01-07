from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QSpinBox, QComboBox, QGroupBox
from PySide6.QtCore import Signal, QSignalBlocker


class SchedulerView(QWidget):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(14)

        self.enable = QCheckBox("Enable auto-clean timer")
        main.addWidget(self.enable)

        row = QHBoxLayout()
        row.addWidget(QLabel("Interval (min)"))
        self.interval = QSpinBox()
        self.interval.setRange(5, 1440)
        row.addWidget(self.interval)
        row.addWidget(QLabel("Profile"))
        self.profile = QComboBox()
        self.profile.addItem("Quick", "quick")
        self.profile.addItem("Custom", "custom")
        row.addWidget(self.profile)
        row.addStretch(1)
        main.addLayout(row)

        cond = QGroupBox("Advanced")
        cond_layout = QVBoxLayout(cond)

        self.ram_enabled = QCheckBox("Clean if RAM% >")
        self.ram_value = QSpinBox()
        self.ram_value.setRange(50, 99)
        row1 = QHBoxLayout()
        row1.addWidget(self.ram_enabled)
        row1.addWidget(self.ram_value)
        row1.addWidget(QLabel("%"))
        row1.addStretch(1)
        cond_layout.addLayout(row1)

        self.temp_enabled = QCheckBox("Clean if Temp >")
        self.temp_value = QSpinBox()
        self.temp_value.setRange(256, 10240)
        row2 = QHBoxLayout()
        row2.addWidget(self.temp_enabled)
        row2.addWidget(self.temp_value)
        row2.addWidget(QLabel("MB"))
        row2.addStretch(1)
        cond_layout.addLayout(row2)

        self.idle_enabled = QCheckBox("Clean if idle >")
        self.idle_value = QSpinBox()
        self.idle_value.setRange(1, 240)
        row3 = QHBoxLayout()
        row3.addWidget(self.idle_enabled)
        row3.addWidget(self.idle_value)
        row3.addWidget(QLabel("min"))
        row3.addStretch(1)
        cond_layout.addLayout(row3)

        main.addWidget(cond)

        self.enable.stateChanged.connect(lambda _=None: self.changed.emit())
        self.interval.valueChanged.connect(lambda _=None: self.changed.emit())
        self.profile.currentIndexChanged.connect(lambda _=None: self.changed.emit())
        self.ram_enabled.stateChanged.connect(lambda _=None: self.changed.emit())
        self.ram_value.valueChanged.connect(lambda _=None: self.changed.emit())
        self.temp_enabled.stateChanged.connect(lambda _=None: self.changed.emit())
        self.temp_value.valueChanged.connect(lambda _=None: self.changed.emit())
        self.idle_enabled.stateChanged.connect(lambda _=None: self.changed.emit())
        self.idle_value.valueChanged.connect(lambda _=None: self.changed.emit())

    def get_state(self):
        profile = self.profile.currentData()
        return {
            "enabled": self.enable.isChecked(),
            "interval_min": self.interval.value(),
            "profile": profile if profile else "quick",
            "conditions": {
                "ram_gt_enabled": self.ram_enabled.isChecked(),
                "ram_gt": self.ram_value.value(),
                "temp_gt_enabled": self.temp_enabled.isChecked(),
                "temp_gt_mb": self.temp_value.value(),
                "idle_gt_enabled": self.idle_enabled.isChecked(),
                "idle_gt_min": self.idle_value.value(),
            },
        }

    def set_state(self, data):
        blockers = [
            QSignalBlocker(self.enable),
            QSignalBlocker(self.interval),
            QSignalBlocker(self.profile),
            QSignalBlocker(self.ram_enabled),
            QSignalBlocker(self.ram_value),
            QSignalBlocker(self.temp_enabled),
            QSignalBlocker(self.temp_value),
            QSignalBlocker(self.idle_enabled),
            QSignalBlocker(self.idle_value),
        ]
        self.enable.setChecked(data.get("enabled", False))
        self.interval.setValue(int(data.get("interval_min", 15)))
        prof = data.get("profile", "quick")
        idx = self.profile.findData(prof)
        if idx >= 0:
            self.profile.setCurrentIndex(idx)
        else:
            self.profile.setCurrentIndex(0)
        cond = data.get("conditions", {})
        self.ram_enabled.setChecked(cond.get("ram_gt_enabled", False))
        self.ram_value.setValue(int(cond.get("ram_gt", 85)))
        self.temp_enabled.setChecked(cond.get("temp_gt_enabled", False))
        self.temp_value.setValue(int(cond.get("temp_gt_mb", 2048)))
        self.idle_enabled.setChecked(cond.get("idle_gt_enabled", False))
        self.idle_value.setValue(int(cond.get("idle_gt_min", 10)))
        del blockers
