# dashboard.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QFont


class Dashboard(QWidget):
    """Glass-style dashboard that appears when user clicks the static robot."""
    def __init__(self, width=360, height=260):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(width, height)

        layout = QVBoxLayout()
        title = QLabel("Tejas • Dashboard")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)

        hint = QLabel("Click a button to run a task")
        hint.setStyleSheet("color: #d1d7dd;")
        layout.addWidget(hint)

        # Example task buttons (wire them to your actual task functions)
        b1 = QPushButton("Open Browser")
        b1.clicked.connect(lambda: print("TODO: open browser"))
        b2 = QPushButton("Decrease Volume")
        b2.clicked.connect(lambda: print("TODO: decrease volume"))

        for b in (b1, b2):
            b.setFixedHeight(36)
            b.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.06);
                    color: white;
                    border: 1px solid rgba(255,255,255,0.07);
                    border-radius: 8px;
                    font-weight: 600;
                }
                QPushButton:hover { background: rgba(255,255,255,0.09); }
            """)
            layout.addWidget(b)

        layout.addStretch()
        self.setLayout(layout)

    def paintEvent(self, ev):
        # Simple frosted glass look: rounded semi-transparent rectangle
        r = self.rect()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(20, 24, 28, 220)  # dark translucent
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(r, 14, 14)
