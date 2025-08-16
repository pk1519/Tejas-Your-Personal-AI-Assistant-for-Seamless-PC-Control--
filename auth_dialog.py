
# auth_dialog.py - Enhanced Authentication Dialog
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QFont, QPainter, QPainterPath

class AuthDialog(QDialog):
    google_auth_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 AI Dashboard - Authentication")
        self.setModal(True)
        self.setFixedSize(450, 600)
        
        # Remove window frame for custom styling
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        self.setup_ui()
        self.apply_styling()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header Section
        header_section = self.create_header_section()
        main_layout.addWidget(header_section)
        
        # Spacer
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Authentication Options
        auth_section = self.create_auth_section()
        main_layout.addWidget(auth_section)
        
        # Spacer
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Loading Section (initially hidden)
        self.loading_section = self.create_loading_section()
        self.loading_section.setVisible(False)
        main_layout.addWidget(self.loading_section)
        
        # Footer
        footer_section = self.create_footer_section()
        main_layout.addWidget(footer_section)
        
        self.setLayout(main_layout)
    
    def create_header_section(self):
        section = QFrame()
        section.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)
        
        # Logo/Icon
        logo = QLabel("🤖")
        logo.setStyleSheet("""
            font-size: 64px;
            background: transparent;
        """)
        logo.setAlignment(Qt.AlignCenter)
        
        # Title
        title = QLabel("AI Dashboard")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            background: transparent;
            margin: 10px 0px;
        """)
        title.setAlignment(Qt.AlignCenter)
        
        # Subtitle
        subtitle = QLabel("Please sign in to continue")
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: rgba(255, 255, 255, 0.7);
            background: transparent;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        section.setLayout(layout)
        return section
    
    def create_auth_section(self):
        section = QFrame()
        section.setStyleSheet("""
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px;
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Google Sign In Button
        self.google_btn = QPushButton("🌐 Continue with Google")
        self.google_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(66, 133, 244, 0.8),
                    stop:1 rgba(52, 168, 83, 0.8));
                color: white;
                border: none;
                border-radius: 15px;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(66, 133, 244, 1.0),
                    stop:1 rgba(52, 168, 83, 1.0));
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                transform: translateY(0px);
            }
        """)
        self.google_btn.setFixedHeight(55)
        self.google_btn.clicked.connect(self.on_google_auth)
        
        # Info text
        info_text = QLabel("🔒 Secure authentication with Google OAuth 2.0")
        info_text.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6);
            font-size: 12px;
            background: transparent;
            margin-top: 10px;
        """)
        info_text.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.google_btn)
        layout.addWidget(info_text)
        
        section.setLayout(layout)
        return section
    
    def create_loading_section(self):
        section = QFrame()
        section.setStyleSheet("""
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.3);
            border-radius: 15px;
            padding: 20px;
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # Loading animation (text-based)
        self.loading_label = QLabel("🔄 Authenticating...")
        self.loading_label.setStyleSheet("""
            color: rgba(255, 193, 7, 1);
            font-size: 16px;
            font-weight: bold;
            background: transparent;
        """)
        self.loading_label.setAlignment(Qt.AlignCenter)
        
        loading_info = QLabel("Please complete the authentication in your browser")
        loading_info.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
            background: transparent;
        """)
        loading_info.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.loading_label)
        layout.addWidget(loading_info)
        
        section.setLayout(layout)
        
        # Animate loading text
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.animate_loading)
        self.loading_states = ["🔄 Authenticating", "🔄 Authenticating.", "🔄 Authenticating..", "🔄 Authenticating..."]
        self.loading_state_index = 0
        
        return section
    
    def create_footer_section(self):
        section = QFrame()
        section.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # Cancel button
        cancel_btn = QPushButton("✕ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(244, 67, 54, 0.1);
                color: rgba(244, 67, 54, 1);
                border: 1px solid rgba(244, 67, 54, 0.3);
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(244, 67, 54, 0.2);
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        # Privacy notice
        privacy_text = QLabel("By signing in, you agree to our privacy policy")
        privacy_text.setStyleSheet("""
            color: rgba(255, 255, 255, 0.4);
            font-size: 10px;
            background: transparent;
        """)
        privacy_text.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(cancel_btn)
        layout.addWidget(privacy_text)
        
        section.setLayout(layout)
        return section
    
    def apply_styling(self):
        """Apply glassmorphism styling to the dialog"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(20, 20, 40, 0.95),
                    stop:0.3 rgba(40, 20, 60, 0.9),
                    stop:0.7 rgba(60, 40, 80, 0.9),
                    stop:1 rgba(80, 60, 40, 0.95));
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 25px;
            }
        """)
    
    def on_google_auth(self):
        """Handle Google authentication button click"""
        self.google_auth_requested.emit()
    
    def show_loading(self):
        """Show loading state"""
        self.loading_section.setVisible(True)
        self.google_btn.setEnabled(False)
        self.loading_timer.start(500)  # Update every 500ms
    
    def hide_loading(self):
        """Hide loading state"""
        self.loading_section.setVisible(False)
        self.google_btn.setEnabled(True)
        self.loading_timer.stop()
    
    def animate_loading(self):
        """Animate loading text"""
        self.loading_label.setText(self.loading_states[self.loading_state_index])
        self.loading_state_index = (self.loading_state_index + 1) % len(self.loading_states)