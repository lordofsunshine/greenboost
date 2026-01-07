from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QListWidget, QCheckBox, QGroupBox
from PySide6.QtCore import Signal
from app.core.profiles import CATEGORIES


class CleaningView(QWidget):
    start_clean = Signal(list)
    deep_clean = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(14)

        title = QLabel("Custom Clean")
        main.addWidget(title)

        box = QGroupBox("Categories")
        box_layout = QVBoxLayout(box)
        self.checks = {}
        for key, meta in CATEGORIES.items():
            chk = QCheckBox(f"{meta['label']} — {meta['note']}")
            self.checks[key] = chk
            box_layout.addWidget(chk)
        main.addWidget(box)

        row = QHBoxLayout()
        self.btn_start = QPushButton("Run")
        self.btn_start.setProperty("role", "primary")
        self.btn_deep = QPushButton("Deep Clean")
        row.addWidget(self.btn_start)
        row.addWidget(self.btn_deep)
        row.addStretch(1)
        main.addLayout(row)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.steps = QListWidget()
        main.addWidget(self.progress)
        main.addWidget(self.steps, 1)

        self.btn_start.clicked.connect(self._on_start)
        self.btn_deep.clicked.connect(lambda _=None: self.deep_clean.emit())

    def _on_start(self):
        selection = [k for k, chk in self.checks.items() if chk.isChecked()]
        self.start_clean.emit(selection)

    def set_selection(self, keys):
        for k, chk in self.checks.items():
            chk.setChecked(k in keys)

    def set_progress(self, value, text=None):
        self.progress.setValue(value)
        if text:
            self.steps.addItem(text)
            self.steps.scrollToBottom()

    def reset_progress(self):
        self.progress.setValue(0)
        self.steps.clear()
