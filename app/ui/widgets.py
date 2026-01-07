from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPalette
from PySide6.QtCore import Qt, QSize, QRect


class CircularGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._title = "Load Index"
        self._accent = QColor("#2FBF67")
        self._diameter = 200
        self.setFixedSize(self._diameter, self._diameter)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def set_value(self, value):
        self._value = max(0, min(100, float(value)))
        self.update()

    def set_title(self, title):
        self._title = title
        self.update()

    def set_accent(self, color):
        self._accent = QColor(color)
        self.update()

    def sizeHint(self):
        return QSize(self._diameter, self._diameter)

    def paintEvent(self, event):
        rect = self.rect().adjusted(12, 12, -12, -12)
        side = min(rect.width(), rect.height())
        square = QRect(0, 0, side, side)
        square.moveCenter(rect.center())
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        base = self.palette().color(QPalette.Text)
        bg_pen = QPen(QColor(base.red(), base.green(), base.blue(), 40), 10)
        painter.setPen(bg_pen)
        painter.drawEllipse(square)
        pen = QPen(self._accent, 10)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        span = int(-self._value / 100 * 360 * 16)
        painter.drawArc(square, 90 * 16, span)
        painter.setPen(base)
        font = QFont(self.font())
        font.setPointSize(22)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, f"{int(self._value)}%")
        painter.setPen(QColor(base.red(), base.green(), base.blue(), 140))
        font2 = QFont(self.font())
        font2.setPointSize(9)
        painter.setFont(font2)
        painter.drawText(self.rect().adjusted(0, 70, 0, 0), Qt.AlignHCenter, self._title)


class StatCard(QWidget):
    def __init__(self, title, value="0%", suffix="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.title_label = QLabel(title)
        self.title_label.setObjectName("muted")
        self.value_label = QLabel(value)
        self.value_label.setProperty("class", "value")
        self.suffix_label = QLabel(suffix)
        self.suffix_label.setObjectName("muted")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)
        layout.addWidget(self.title_label)
        row = QHBoxLayout()
        row.addWidget(self.value_label)
        row.addWidget(self.suffix_label)
        row.addStretch(1)
        layout.addLayout(row)

    def set_value(self, value, suffix=""):
        self.value_label.setText(value)
        self.suffix_label.setText(suffix)
