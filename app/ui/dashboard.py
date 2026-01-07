from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve
from .widgets import CircularGauge, StatCard


class DashboardView(QWidget):
    quick_clean = Signal()
    custom_clean = Signal()
    show_formula = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(14)

        top = QHBoxLayout()
        top.setSpacing(16)
        self.gauge = CircularGauge()
        top.addWidget(self.gauge, 0, Qt.AlignLeft | Qt.AlignVCenter)

        cards_col = QVBoxLayout()
        cards_col.setSpacing(12)
        self.ram_card = StatCard("RAM used", "0%")
        self.pagefile_card = StatCard("Pagefile used", "0%")
        self.disk_card = StatCard("Disk C:", "0%")
        self.temp_card = StatCard("Temp size", "0", "MB")
        cards_col.addWidget(self.ram_card)
        cards_col.addWidget(self.pagefile_card)
        cards_col.addWidget(self.disk_card)
        cards_col.addWidget(self.temp_card)
        top.addLayout(cards_col, 1)
        main.addLayout(top)

        btns = QHBoxLayout()
        self.btn_quick = QPushButton("Quick Clean")
        self.btn_quick.setProperty("role", "primary")
        self.btn_custom = QPushButton("Custom Clean...")
        self.btn_formula = QPushButton("How is it calculated?")
        self.btn_formula.setProperty("role", "ghost")
        btns.addWidget(self.btn_quick)
        btns.addWidget(self.btn_custom)
        btns.addWidget(self.btn_formula)
        btns.addStretch(1)
        main.addLayout(btns)

        self.last_label = QLabel("Last clean: no data")
        self.last_label.setObjectName("muted")
        main.addWidget(self.last_label)

        self.breakdown_label = QLabel("")
        self.breakdown_label.setObjectName("muted")
        main.addWidget(self.breakdown_label)

        self.btn_quick.clicked.connect(lambda _=None: self.quick_clean.emit())
        self.btn_custom.clicked.connect(lambda _=None: self.custom_clean.emit())
        self.btn_formula.clicked.connect(lambda _=None: self.show_formula.emit())

        self._quick_text = "Quick Clean"
        self._quick_effect = QGraphicsOpacityEffect(self.btn_quick)
        self.btn_quick.setGraphicsEffect(self._quick_effect)
        self._quick_anim = QPropertyAnimation(self._quick_effect, b"opacity")
        self._quick_anim.setDuration(700)
        self._quick_anim.setStartValue(1.0)
        self._quick_anim.setEndValue(0.6)
        self._quick_anim.setEasingCurve(QEasingCurve.InOutSine)
        self._quick_anim.setLoopCount(-1)
        self._cleaning = False

    def update_metrics(self, metrics):
        self.gauge.set_value(metrics.get("index", 0))
        self.ram_card.set_value(f"{metrics.get('ram', 0)}%")
        self.pagefile_card.set_value(f"{metrics.get('pagefile', 0)}%")
        self.disk_card.set_value(f"{metrics.get('disk', 0)}%")
        self.temp_card.set_value(str(metrics.get("temp_mb", 0)), "MB")

    def update_breakdown(self, ram, pagefile, disk, temp_score):
        self.breakdown_label.setText(
            f"Contrib: RAM {ram}% | Pagefile {pagefile}% | Disk C {disk}% | Temp {temp_score}%"
        )

    def update_last_clean(self, time_text, freed_mb, profile):
        if not time_text:
            self.last_label.setText("Last clean: no data")
        else:
            self.last_label.setText(f"Last clean: {time_text}, freed {freed_mb} MB ({profile})")

    def set_cleaning(self, active):
        if self._cleaning == active:
            return
        self._cleaning = active
        if active:
            self.btn_quick.setText("Cleaning...")
            self._quick_anim.start()
        else:
            self._quick_anim.stop()
            self._quick_effect.setOpacity(1.0)
            self.btn_quick.setText(self._quick_text)
