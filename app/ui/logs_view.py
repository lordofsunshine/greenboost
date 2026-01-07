from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QComboBox, QPushButton
from PySide6.QtCore import Signal


class LogsView(QWidget):
    refresh_requested = Signal()
    open_folder = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(12)

        row = QHBoxLayout()
        row.addWidget(QLabel("Filter"))
        self.filter = QComboBox()
        self.filter.addItem("All", "all")
        self.filter.addItem("Info", "info")
        self.filter.addItem("Warning", "warning")
        self.filter.addItem("Error", "error")
        row.addWidget(self.filter)
        self.btn_refresh = QPushButton("Refresh")
        row.addWidget(self.btn_refresh)
        self.btn_open = QPushButton("Open logs folder")
        row.addWidget(self.btn_open)
        row.addStretch(1)
        main.addLayout(row)

        self.list = QListWidget()
        main.addWidget(self.list, 1)

        self.filter.currentIndexChanged.connect(lambda _=None: self.refresh_requested.emit())
        self.btn_refresh.clicked.connect(lambda _=None: self.refresh_requested.emit())
        self.btn_open.clicked.connect(lambda _=None: self.open_folder.emit())

    def set_logs(self, lines):
        self.list.clear()
        for line in lines:
            self.list.addItem(line)
