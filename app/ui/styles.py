def get_qss(theme):
    if theme == "dark":
        colors = {
            "bg": "#101214",
            "bg2": "#14181C",
            "panel": "#171A1D",
            "card": "#1C2024",
            "text": "#E7EAED",
            "muted": "#9AA3AB",
            "accent": "#32C46A",
            "accent_soft": "#1F3A2B",
            "border": "#2A2F34",
            "danger": "#E35B5B",
        }
    else:
        colors = {
            "bg": "#F6F7F9",
            "bg2": "#EEF2F5",
            "panel": "#FFFFFF",
            "card": "#FFFFFF",
            "text": "#1B1F23",
            "muted": "#5E6B76",
            "accent": "#2FBF67",
            "accent_soft": "#E6F6EC",
            "border": "#E1E6EB",
            "danger": "#D84B4B",
        }
    return f"""
    * {{
        font-family: 'Segoe UI Variable', 'Segoe UI', 'Arial';
        color: {colors['text']};
    }}
    QMainWindow {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {colors['bg']}, stop:1 {colors['bg2']});
    }}
    QDialog, QMessageBox {{
        background: {colors['panel']};
    }}
    QMessageBox QLabel {{
        color: {colors['text']};
    }}
    QWidget#nav {{
        background: {colors['panel']};
        border: 1px solid {colors['border']};
        border-radius: 18px;
    }}
    QWidget#panel {{
        background: {colors['panel']};
        border: 1px solid {colors['border']};
        border-radius: 14px;
    }}
    QWidget#card {{
        background: {colors['card']};
        border: 1px solid {colors['border']};
        border-radius: 16px;
    }}
    QLabel#muted {{
        color: {colors['muted']};
    }}
    QLabel#title {{
        font-size: 18px;
        font-weight: 600;
    }}
    QLabel[class='value'] {{
        font-size: 18px;
        font-weight: 600;
    }}
    QPushButton {{
        background: {colors['panel']};
        border: 1px solid {colors['border']};
        border-radius: 10px;
        padding: 8px 14px;
    }}
    QPushButton:hover {{
        border-color: {colors['accent']};
    }}
    QPushButton[role='primary'] {{
        background: {colors['accent']};
        color: #ffffff;
        border: 1px solid {colors['accent']};
    }}
    QPushButton[role='primary']:hover {{
        background: {colors['accent']};
    }}
    QPushButton[role='ghost'] {{
        background: transparent;
        border: 1px solid transparent;
    }}
    QPushButton[nav='true'] {{
        background: transparent;
        border: 1px solid transparent;
        text-align: left;
        padding: 8px 10px;
        border-radius: 10px;
    }}
    QPushButton[nav='true']:hover {{
        background: {colors['accent_soft']};
        border-color: {colors['accent_soft']};
    }}
    QPushButton[nav='true'][active='true'] {{
        background: {colors['accent_soft']};
        border-color: {colors['accent']};
    }}
    QPushButton[role='danger'] {{
        background: {colors['danger']};
        color: #ffffff;
        border: 1px solid {colors['danger']};
    }}
    QProgressBar {{
        background: {colors['panel']};
        border: 1px solid {colors['border']};
        border-radius: 8px;
        text-align: center;
        height: 10px;
    }}
    QProgressBar::chunk {{
        background: {colors['accent']};
        border-radius: 8px;
    }}
    QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {{
        background: {colors['panel']};
        border: 1px solid {colors['border']};
        border-radius: 8px;
        padding: 6px 8px;
    }}
    QListWidget {{
        background: {colors['panel']};
        border: 1px solid {colors['border']};
        border-radius: 10px;
    }}
    QGroupBox {{
        border: 1px solid {colors['border']};
        border-radius: 10px;
        margin-top: 14px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 6px 0 6px;
    }}
    QCheckBox {{
        spacing: 8px;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {colors['border']};
        border-radius: 5px;
    }}
    """
