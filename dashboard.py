import sys
import os
import json
import pyttsx3
import psutil
from datetime import datetime, timedelta
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPalette, QColor, QFont, QPainter, QPen, QBrush, QLinearGradient, QPixmap, QPainterPath
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout,
    QWidget, QLineEdit, QLabel, QFrame, QGridLayout, QSpacerItem, QSizePolicy, QScrollArea, QStackedWidget,
    QComboBox, QDateTimeEdit, QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QProgressBar, QTableWidget,
    QTableWidgetItem, QHeaderView, QColorDialog, QCheckBox
)
from ai_core import handle_task, llm_fallback, recognize_voice, get_network_info
from auth_manager import AuthManager
from auth_dialog import AuthDialog
import random

class GlassFrame(QFrame):
    """Base glass frame with glassmorphism effect"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 20px;
                backdrop-filter: blur(20px);
            }
        """)

class GlassButton(QPushButton):
    """Glass-themed button"""
    def __init__(self, text="", icon="", parent=None):
        super().__init__(text, parent)
        if icon:
            self.setText(f"{icon} {text}" if text else icon)
        self.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.15);
                transform: translateY(0px);
            }
        """)

class UserSidebar(GlassFrame):
    """Left sidebar with user panel and navigation"""
    
    # Signals
    logout_requested = pyqtSignal()
    nav_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320)
        self.user_data = None
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 30, 25, 30)
        
        # User Profile Section
        self.profile_section = self.create_profile_section()
        layout.addWidget(self.profile_section)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background: rgba(255, 255, 255, 0.1); border: none; height: 1px;")
        layout.addWidget(divider)
        
        # Navigation Section
        self.nav_section = self.create_nav_section()
        layout.addWidget(self.nav_section)
        
        layout.addStretch()
        
        # Logout Button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background: rgba(244, 67, 54, 0.9);
                color: white;
                border: 1px solid rgba(244, 67, 54, 0.3);
                border-radius: 15px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 500;
                text-align: center;
            }
            QPushButton:hover {
                background: rgba(244, 67, 54, 1.0);
                border: 1px solid rgba(244, 67, 54, 0.5);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: rgba(211, 47, 47, 1.0);
                transform: translateY(0px);
            }
        """)
        logout_btn.setFixedHeight(45)
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)
        
        # Removed footer per requirements
        
        self.setLayout(layout)
    
    def create_profile_section(self):
        section = QWidget()
        section.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Profile Header
        header = QLabel("👤 User Panel")
        header.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
            padding: 10px 0px;
        """)
        
        # User Avatar & Info (will be updated with real user data)
        self.user_info = QFrame()
        self.user_info.setStyleSheet("""
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 15px;
        """)
        
        self.user_layout = QHBoxLayout()
        
        # Avatar
        self.avatar = QLabel("👨‍💻")
        self.avatar.setStyleSheet("""
            background: rgba(100, 181, 246, 0.2);
            border: 2px solid rgba(100, 181, 246, 0.3);
            border-radius: 30px;
            font-size: 24px;
            padding: 15px;
        """)
        self.avatar.setFixedSize(60, 60)
        self.avatar.setAlignment(Qt.AlignCenter)
        
        # User Details
        details_layout = QVBoxLayout()
        self.user_name = QLabel("Guest User")
        self.user_name.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")
        
        self.user_status = QLabel("🔐 Please Sign In")
        self.user_status.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 12px; background: transparent;")
        
        details_layout.addWidget(self.user_name)
        details_layout.addWidget(self.user_status)
        
        self.user_layout.addWidget(self.avatar)
        self.user_layout.addSpacing(15)
        self.user_layout.addLayout(details_layout)
        self.user_layout.addStretch()
        
        self.user_info.setLayout(self.user_layout)
        
        layout.addWidget(header)
        layout.addWidget(self.user_info)
        
        section.setLayout(layout)
        return section
    
    def update_user_info(self, user_data):
        """Update user interface with authenticated user data"""
        self.user_data = user_data
        if user_data:
            self.user_name.setText(user_data.get('name', 'Unknown User'))
            self.user_status.setText("🟢 Online")
            
            # Update avatar if picture URL is provided
            picture = user_data.get('picture', '👤')
            if picture and not picture.startswith('http'):
                self.avatar.setText(picture)
        else:
            self.user_name.setText("Guest User")
            self.user_status.setText("🔐 Please Sign In")
            self.avatar.setText("👨‍💻")
    
    def create_nav_section(self):
        section = QWidget()
        section.setStyleSheet("background: transparent;")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        header = QLabel("🧭 Tools")
        header.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            background: transparent;
            padding: 10px 0px;
        """)
        layout.addWidget(header)
        
        # Navigation buttons with icons
        nav_items = [
            ("Chat", "💬", "chat"),
            ("Reminder", "🔔", "reminder"),
            ("Filelock", "🔒", "filelock"),
            ("Performance", "⚡", "performance"),
            ("Task Manager", "📋", "taskmanager"),
            ("Storage", "💾", "storage"),
            ("Theme", "🎨", "theme"),
        ]
        self.nav_buttons = {}
        for text, icon, key in nav_items:
            btn = GlassButton(text, icon)
            btn.setFixedHeight(45)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, k=key: self.on_nav_clicked(k))
            layout.addWidget(btn)
            self.nav_buttons[key] = btn
        
        # Default highlight Chat
        self.set_active_nav("chat")
        
        section.setLayout(layout)
        return section
    
    def set_active_nav(self, key):
        for k, b in getattr(self, 'nav_buttons', {}).items():
            b.setChecked(k == key)
            if k == key:
                b.setStyleSheet(b.styleSheet() + "\nQPushButton:checked { background: rgba(100, 181, 246, 0.25); border: 1px solid rgba(100, 181, 246, 0.5); }")
            else:
                # reset to base style
                b.setStyleSheet("""
                    QPushButton {
                        background: rgba(255, 255, 255, 0.1);
                        color: white;
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        border-radius: 15px;
                        padding: 12px 20px;
                        font-size: 14px;
                        font-weight: 500;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background: rgba(255, 255, 255, 0.2);
                        border: 1px solid rgba(255, 255, 255, 0.3);
                        transform: translateY(-2px);
                    }
                    QPushButton:pressed {
                        background: rgba(255, 255, 255, 0.15);
                        transform: translateY(0px);
                    }
                """)
    
    def on_nav_clicked(self, key):
        self.set_active_nav(key)
        self.nav_selected.emit(key)
    
    def create_settings_section(self):
        # Deprecated in enhanced design
        return QWidget()

class ChatInterface(GlassFrame):
    """Center chat interface with AI"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_dashboard = parent
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Chat Header
        self.header = self.create_chat_header()
        layout.addWidget(self.header)
        
        # Chat Display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                color: white;
                font-size: 14px;
                line-height: 1.6;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 5px;
            }
        """)
        
        # Welcome message
        self.chat_display.append("🤖 <b>AI Assistant:</b> Hello! I'm your AI assistant. You can chat with me using text or voice. How can I help you today?")
        
        layout.addWidget(self.chat_display)
        
        # Input Section
        input_section = self.create_input_section()
        layout.addWidget(input_section)
        
        self.setLayout(layout)
    
    def create_chat_header(self):
        header = QFrame()
        header.setStyleSheet("background: transparent;")
        header.setFixedHeight(60)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # AI Status
        ai_status = QLabel("🤖 AI Assistant")
        ai_status.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            background: transparent;
        """)
        
        # Status indicator (this will become logout button)
        self.status_btn = QPushButton("🟢 Active")
        self.status_btn.setStyleSheet("""
            QPushButton {
                color: rgba(76, 175, 80, 1);
                font-size: 12px;
                background: rgba(76, 175, 80, 0.1);
                padding: 8px 16px;
                border: 1px solid rgba(76, 175, 80, 0.3);
                border-radius: 15px;
            }
            QPushButton:hover {
                background: rgba(76, 175, 80, 0.2);
                cursor: pointer;
            }
        """)
        
        layout.addWidget(ai_status)
        layout.addStretch()
        layout.addWidget(self.status_btn)
        
        header.setLayout(layout)
        return header
    
    def update_status_button(self, is_authenticated, user_data=None):
        """Update status button based on authentication state"""
        if is_authenticated and user_data:
            # Show logout button
            self.status_btn.setText("🚪 Logout")
            self.status_btn.setStyleSheet("""
                QPushButton {
                    color: rgba(244, 67, 54, 1);
                    font-size: 12px;
                    background: rgba(244, 67, 54, 0.1);
                    padding: 8px 16px;
                    border: 1px solid rgba(244, 67, 54, 0.3);
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background: rgba(244, 67, 54, 0.2);
                    cursor: pointer;
                }
            """)
            # Connect to logout function in parent dashboard
            if self.parent_dashboard:
                try:
                    self.status_btn.clicked.disconnect()
                except:
                    pass
                self.status_btn.clicked.connect(self.parent_dashboard.handle_logout)
        else:
            # Show sign in button
            self.status_btn.setText("🔐 Sign In")
            self.status_btn.setStyleSheet("""
                QPushButton {
                    color: rgba(255, 193, 7, 1);
                    font-size: 12px;
                    background: rgba(255, 193, 7, 0.1);
                    padding: 8px 16px;
                    border: 1px solid rgba(255, 193, 7, 0.3);
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background: rgba(255, 193, 7, 0.2);
                    cursor: pointer;
                }
            """)
            # Connect to sign in function in parent dashboard
            if self.parent_dashboard:
                try:
                    self.status_btn.clicked.disconnect()
                except:
                    pass
                self.status_btn.clicked.connect(self.parent_dashboard.show_auth_dialog)
    
    def create_input_section(self):
        section = QFrame()
        section.setStyleSheet("""
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 15px;
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Text input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(15)
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("💬 Type your message here...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                padding: 12px 16px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(100, 181, 246, 0.5);
                background: rgba(255, 255, 255, 0.15);
            }
        """)
        self.text_input.setFixedHeight(45)
        # Connect to parent dashboard methods if parent exists
        if self.parent_dashboard:
            self.text_input.returnPressed.connect(self.parent_dashboard.on_text_submit)
        
        # Send button
        send_btn = QPushButton("📤")
        send_btn.setStyleSheet("""
            QPushButton {
                background: rgba(100, 181, 246, 0.8);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                padding: 8px;
            }
            QPushButton:hover {
                background: rgba(100, 181, 246, 1.0);
            }
        """)
        send_btn.setFixedSize(45, 45)
        if self.parent_dashboard:
            send_btn.clicked.connect(self.parent_dashboard.on_text_submit)
        
        input_layout.addWidget(self.text_input)
        input_layout.addWidget(send_btn)
        
        # Voice controls row with left/right alignment
        voice_row = QHBoxLayout()
        voice_row.setSpacing(10)
        
        self.voice_btn = GlassButton("🎤 Voice Input")
        if self.parent_dashboard:
            self.voice_btn.clicked.connect(self.parent_dashboard.on_voice_input)
        self.voice_btn.setFixedHeight(40)
        
        voice_row.addWidget(self.voice_btn)
        voice_row.addStretch()
        
        self.speech_toggle = GlassButton("🔊 Voice Output: OFF")
        if self.parent_dashboard:
            self.speech_toggle.clicked.connect(self.parent_dashboard.toggle_speech)
        self.speech_toggle.setFixedHeight(40)
        
        voice_row.addWidget(self.speech_toggle)
        
        layout.addLayout(input_layout)
        layout.addLayout(voice_row)
        
        section.setLayout(layout)
        return section

class GlassDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🤖 AI Glass Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize authentication
        self.auth_manager = AuthManager()
        self.auth_dialog = None
        
        # Initialize AI components
        self.enable_speech_output = False
        self.tts_engine = pyttsx3.init()
        
        # Persistence files
        self.reminders_file = os.path.join(os.getcwd(), 'reminders.json')
        self.settings_file = os.path.join(os.getcwd(), 'ui_settings.json')
        
        # Set up main layout
        self.setup_ui()
        
        # Apply glass theme
        self.apply_glass_theme()
        
        # Connect authentication signals
        self.setup_auth_connections()
        
        # Check initial authentication state
        self.check_initial_auth()
    
    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left Sidebar - User Panel
        self.sidebar = UserSidebar()
        self.sidebar.nav_selected.connect(self.on_nav_selected)
        self.sidebar.logout_requested.connect(self.handle_logout)
        
        # Center - Stacked Main Content
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        
        # Pages
        self.chat_interface = ChatInterface(self)
        self.reminder_panel = ReminderPanel(self)
        self.filelock_panel = FilelockPanel(self)
        self.performance_panel = PerformancePanel(self)
        self.task_manager_panel = TaskManagerPanel(self)
        self.storage_panel = StoragePanel(self)
        self.theme_panel = ThemePanel(self)
        
        self.stack.addWidget(self.chat_interface)      # index 0 - key 'chat'
        self.stack.addWidget(self.reminder_panel)      # index 1 - key 'reminder'
        self.stack.addWidget(self.filelock_panel)      # index 2 - key 'filelock'
        self.stack.addWidget(self.performance_panel)   # index 3 - key 'performance'
        self.stack.addWidget(self.task_manager_panel)  # index 4 - key 'taskmanager'
        self.stack.addWidget(self.storage_panel)       # index 5 - key 'storage'
        self.stack.addWidget(self.theme_panel)         # index 6 - key 'theme'
        
        # Add to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack, 1)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def setup_auth_connections(self):
        """Setup authentication signal connections"""
        self.auth_manager.login_successful.connect(self.on_login_success)
        self.auth_manager.logout_successful.connect(self.on_logout_success)
        self.auth_manager.auth_required.connect(self.show_auth_dialog)
    
    def check_initial_auth(self):
        """Check if user is already authenticated on startup"""
        if self.auth_manager.is_user_authenticated():
            user_data = self.auth_manager.get_user_info()
            self.on_login_success(user_data)
    
    def show_auth_dialog(self):
        """Show authentication dialog"""
        if not self.auth_dialog:
            self.auth_dialog = AuthDialog(self)
            self.auth_dialog.google_auth_requested.connect(self.handle_google_auth)
        
        self.auth_dialog.hide_loading()
        self.auth_dialog.exec_()
    
    def handle_google_auth(self):
        """Handle Google authentication request"""
        if self.auth_dialog:
            self.auth_dialog.show_loading()
        
        # Start authentication process
        self.auth_manager.initiate_google_auth()
        
        # Close dialog after authentication attempt
        if self.auth_dialog:
            self.auth_dialog.accept()
    
    def on_login_success(self, user_data):
        """Handle successful login"""
        # Update sidebar with user info
        self.sidebar.update_user_info(user_data)
        
        # Update chat interface status button
        self.chat_interface.update_status_button(True, user_data)
        
        # Welcome message
        welcome_msg = f"🎉 <b>Welcome back, {user_data.get('name', 'User')}!</b> You are now signed in."
        self.chat_interface.chat_display.append(f"<div style='color: #4CAF50;'>{welcome_msg}</div>")
        
        # Scroll to bottom
        self.chat_interface.chat_display.verticalScrollBar().setValue(
            self.chat_interface.chat_display.verticalScrollBar().maximum()
        )
    
    def on_logout_success(self):
        """Handle successful logout"""
        # Update sidebar
        self.sidebar.update_user_info(None)
        
        # Update chat interface status button
        self.chat_interface.update_status_button(False)
        
        # Goodbye message
        goodbye_msg = "👋 <b>You have been signed out.</b> Sign in again to continue using the dashboard."
        self.chat_interface.chat_display.append(f"<div style='color: #FF9800;'>{goodbye_msg}</div>")
        
        # Return to Chat page
        self.on_nav_selected('chat')
        
        # Scroll to bottom
        self.chat_interface.chat_display.verticalScrollBar().setValue(
            self.chat_interface.chat_display.verticalScrollBar().maximum()
        )
    
    def handle_logout(self):
        """Handle logout button click"""
        self.auth_manager.logout()
    
    def apply_glass_theme(self):
        """Apply glassmorphism theme to the entire window"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(35, 0, 60, 0.98),
                    stop:0.4 rgba(70, 0, 90, 0.94),
                    stop:0.8 rgba(20, 0, 40, 0.96),
                    stop:1 rgba(10, 0, 25, 0.98));
            }
            QWidget {
                color: white;
                font-family: "Segoe UI", "Inter", Arial;
            }
        """)
    
    def on_text_submit(self):
        """Handle text input submission"""
        # Check if user is authenticated
        if not self.auth_manager.is_user_authenticated():
            self.chat_interface.chat_display.append(
                "<div style='color: #FF6B6B;'><b>🔐 Authentication Required:</b> Please sign in to use the AI assistant.</div>"
            )
            self.show_auth_dialog()
            return
        
        user_text = self.chat_interface.text_input.text().strip()
        if user_text:
            # Display user message
            self.chat_interface.chat_display.append(f"<div style='color: #64B5F6;'><b>👤 You:</b> {user_text}</div>")
            
            # Get AI response
            try:
                ai_reply = handle_task(user_text, llm_fallback_func=llm_fallback)
                self.chat_interface.chat_display.append(f"<div style='color: #4CAF50;'><b>🤖 AI:</b> {ai_reply}</div>")
                
                # Speak if enabled
                if self.enable_speech_output:
                    self.speak(ai_reply)
                    
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                self.chat_interface.chat_display.append(f"<div style='color: #FF6B6B;'><b>❌ Error:</b> {error_msg}</div>")
            
            # Clear input
            self.chat_interface.text_input.clear()
            
            # Scroll to bottom
            self.chat_interface.chat_display.verticalScrollBar().setValue(
                self.chat_interface.chat_display.verticalScrollBar().maximum()
            )
    
    def on_voice_input(self):
        """Handle voice input"""
        # Check if user is authenticated
        if not self.auth_manager.is_user_authenticated():
            self.chat_interface.chat_display.append(
                "<div style='color: #FF6B6B;'><b>🔐 Authentication Required:</b> Please sign in to use voice input.</div>"
            )
            self.show_auth_dialog()
            return
        
        self.chat_interface.chat_display.append("<div style='color: #FFD700;'><b>🎤 Listening...</b> Speak now!</div>")
        self.chat_interface.repaint()
        
        try:
            voice_text = recognize_voice(duration=5)
            if voice_text:
                # Display what was heard
                self.chat_interface.chat_display.append(f"<div style='color: #64B5F6;'><b>🗣️ You said:</b> {voice_text}</div>")
                
                # Get AI response
                ai_reply = handle_task(voice_text, llm_fallback_func=llm_fallback)
                self.chat_interface.chat_display.append(f"<div style='color: #4CAF50;'><b>🤖 AI:</b> {ai_reply}</div>")
                
                # Always speak voice responses
                self.speak(ai_reply)
            else:
                self.chat_interface.chat_display.append("<div style='color: #FF9800;'><b>⚠️ No speech detected.</b> Please try again.</div>")
                
        except Exception as e:
            error_msg = f"Voice recognition error: {str(e)}"
            self.chat_interface.chat_display.append(f"<div style='color: #FF6B6B;'><b>❌ Error:</b> {error_msg}</div>")
        
        # Scroll to bottom
        self.chat_interface.chat_display.verticalScrollBar().setValue(
            self.chat_interface.chat_display.verticalScrollBar().maximum()
        )
    
    def toggle_speech(self):
        """Toggle speech output on/off"""
        self.enable_speech_output = not self.enable_speech_output
        status = "ON" if self.enable_speech_output else "OFF"
        self.chat_interface.speech_toggle.setText(f"🔊 Voice Output: {status}")
        
        # Update button style based on state
        if self.enable_speech_output:
            self.chat_interface.speech_toggle.setStyleSheet("""
                QPushButton {
                    background: rgba(76, 175, 80, 0.3);
                    color: white;
                    border: 1px solid rgba(76, 175, 80, 0.5);
                    border-radius: 15px;
                    padding: 12px 20px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: rgba(76, 175, 80, 0.4);
                }
            """)
        else:
            self.chat_interface.speech_toggle.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.1);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 15px;
                    padding: 12px 20px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.2);
                }
            """)
        
        # Notify in chat
        self.chat_interface.chat_display.append(f"<div style='color: #FFD700;'><b>🔄 Voice output {status.lower()}.</b></div>")
        
        # Persist preference
        self._save_settings({"voice_output": self.enable_speech_output})
    
    def speak(self, text):
        """Convert text to speech"""
        if text and self.tts_engine and self.enable_speech_output:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Speech error: {e}")
    
    # ----------------------------
    # Persistence helpers
    # ----------------------------
    def _load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_settings(self, updates: dict):
        current = self._load_settings()
        current.update(updates)
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(current, f, indent=2)
        except Exception:
            pass
    
    # ----------------------------
    # Navigation handling
    # ----------------------------
    def on_nav_selected(self, key: str):
        mapping = {
            'chat': 0,
            'reminder': 1,
            'filelock': 2,
            'performance': 3,
            'taskmanager': 4,
            'storage': 5,
            'theme': 6,
        }
        index = mapping.get(key, 0)
        self.stack.setCurrentIndex(index)
        # Lazy refresh panels if needed
        if key == 'performance':
            self.performance_panel.start_updates()
        else:
            self.performance_panel.stop_updates()
        if key == 'taskmanager':
            self.task_manager_panel.refresh_processes()
        if key == 'storage':
            self.storage_panel.refresh_partitions()

# ----------------------------
# Tool Panels
# ----------------------------
class SectionHeader(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        self.setStyleSheet("color: white; font-size: 20px; font-weight: 700; background: transparent;")

class ReminderPanel(GlassFrame):
    def __init__(self, parent: 'GlassDashboard'):
        super().__init__(parent)
        self.parent_dashboard = parent
        self.reminders = []
        self._load_reminders()
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        layout.addWidget(SectionHeader("🔔 Reminder"))
        
        form = QHBoxLayout()
        self.reminder_text = QLineEdit()
        self.reminder_text.setPlaceholderText("Reminder text…")
        self.reminder_category = QComboBox()
        self.reminder_category.addItems(["Personal", "Work", "Important"])
        self.reminder_time = QDateTimeEdit()
        self.reminder_time.setCalendarPopup(True)
        self.reminder_time.setDateTime(datetime.now() + timedelta(minutes=5))
        add_btn = GlassButton("Add", "➕")
        add_btn.clicked.connect(self.add_reminder)
        for w in [self.reminder_text, self.reminder_category, self.reminder_time, add_btn]:
            if isinstance(w, QLineEdit):
                w.setStyleSheet("QLineEdit { background: rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); border-radius:10px; padding:10px; color:white; }")
            form.addWidget(w)
        layout.addLayout(form)
        
        self.reminder_list = QListWidget()
        self.reminder_list.setStyleSheet("QListWidget { background: rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:12px; color:white; }")
        layout.addWidget(self.reminder_list, 1)
        
        actions = QHBoxLayout()
        del_btn = GlassButton("Delete", "🗑️")
        del_btn.clicked.connect(self.delete_selected)
        edit_btn = GlassButton("Edit", "✏️")
        edit_btn.clicked.connect(self.edit_selected)
        actions.addWidget(edit_btn)
        actions.addWidget(del_btn)
        actions.addStretch()
        layout.addLayout(actions)
        
        self.setLayout(layout)
        self.refresh_list()
        
        # Notification timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_notifications)
        self.timer.start(30000)  # every 30s
    
    def _load_reminders(self):
        try:
            if os.path.exists(self.parent_dashboard.reminders_file):
                with open(self.parent_dashboard.reminders_file, 'r', encoding='utf-8') as f:
                    self.reminders = json.load(f)
        except Exception:
            self.reminders = []
    
    def _save_reminders(self):
        try:
            with open(self.parent_dashboard.reminders_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, indent=2)
        except Exception:
            pass
    
    def add_reminder(self):
        text = self.reminder_text.text().strip()
        if not text:
            return
        item = {
            'text': text,
            'category': self.reminder_category.currentText(),
            'time': self.reminder_time.dateTime().toString(Qt.ISODate),
            'done': False
        }
        self.reminders.append(item)
        self._save_reminders()
        self.refresh_list()
        self.reminder_text.clear()
    
    def refresh_list(self):
        self.reminder_list.clear()
        for r in self.reminders:
            dt = r.get('time', '')
            display = f"[{r.get('category')}] {r.get('text')} — {dt}"
            lw = QListWidgetItem(display)
            self.reminder_list.addItem(lw)
    
    def delete_selected(self):
        row = self.reminder_list.currentRow()
        if row >= 0:
            self.reminders.pop(row)
            self._save_reminders()
            self.refresh_list()
    
    def edit_selected(self):
        row = self.reminder_list.currentRow()
        if row < 0:
            return
        r = self.reminders[row]
        self.reminder_text.setText(r.get('text',''))
        cat = r.get('category','Personal')
        self.reminder_category.setCurrentText(cat)
        try:
            dt = datetime.fromisoformat(r.get('time').replace('Z',''))
        except Exception:
            dt = datetime.now()
        self.reminder_time.setDateTime(dt)
        # remove and re-add upon save
        self.reminders.pop(row)
        self._save_reminders()
        self.refresh_list()
    
    def check_notifications(self):
        now = datetime.now()
        triggered = []
        for idx, r in enumerate(self.reminders):
            try:
                dt = datetime.fromisoformat(r.get('time').replace('Z',''))
            except Exception:
                continue
            if dt <= now and not r.get('done'):
                triggered.append((idx, r))
        for idx, r in triggered:
            r['done'] = True
            self._notify(f"Reminder: {r.get('text')} ({r.get('category')})")
        if triggered:
            self._save_reminders()
            self.refresh_list()
    
    def _notify(self, message: str):
        # Show in chat and dialog
        if self.parent_dashboard:
            self.parent_dashboard.chat_interface.chat_display.append(
                f"<div style='color:#FFD700;'><b>🔔 {message}</b></div>"
            )
        QMessageBox.information(self, "Reminder", message)

class FilelockPanel(GlassFrame):
    def __init__(self, parent: 'GlassDashboard'):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(25,25,25,25)
        layout.setSpacing(15)
        layout.addWidget(SectionHeader("🔒 Filelock"))
        
        path_row = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select a file to encrypt/decrypt…")
        browse = GlassButton("Browse", "📂")
        browse.clicked.connect(self.browse_file)
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(browse)
        
        pass_row = QHBoxLayout()
        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("Password (used to derive key)")
        self.pass_edit.setEchoMode(QLineEdit.Password)
        pass_row.addWidget(self.pass_edit, 1)
        
        btn_row = QHBoxLayout()
        enc = GlassButton("Encrypt", "🛡️")
        dec = GlassButton("Decrypt", "🔓")
        enc.clicked.connect(self.encrypt_file)
        dec.clicked.connect(self.decrypt_file)
        btn_row.addWidget(enc)
        btn_row.addWidget(dec)
        btn_row.addStretch()
        
        info = QLabel("Note: Simple XOR-based demo encryption. For real security, integrate a proven crypto library.")
        info.setStyleSheet("color: rgba(255,255,255,0.6);")
        
        layout.addLayout(path_row)
        layout.addLayout(pass_row)
        layout.addLayout(btn_row)
        layout.addWidget(info)
        
        self.setLayout(layout)
    
    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", os.getcwd())
        if path:
            self.path_edit.setText(path)
    
    def _xor_data(self, data: bytes, key: bytes) -> bytes:
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    
    def _derive_key(self, password: str) -> bytes:
        import hashlib
        return hashlib.sha256(password.encode('utf-8')).digest()
    
    def encrypt_file(self):
        path = self.path_edit.text().strip()
        pwd = self.pass_edit.text()
        if not (path and pwd and os.path.isfile(path)):
            QMessageBox.warning(self, "Filelock", "Select a valid file and enter password")
            return
        try:
            with open(path, 'rb') as f:
                data = f.read()
            key = self._derive_key(pwd)
            enc = self._xor_data(data, key)
            out = path + ".xenc"
            with open(out, 'wb') as f:
                f.write(enc)
            QMessageBox.information(self, "Filelock", f"Encrypted -> {out}")
        except Exception as e:
            QMessageBox.critical(self, "Filelock", f"Error: {e}")
    
    def decrypt_file(self):
        path = self.path_edit.text().strip()
        pwd = self.pass_edit.text()
        if not (path and pwd and os.path.isfile(path)):
            QMessageBox.warning(self, "Filelock", "Select a valid file and enter password")
            return
        try:
            with open(path, 'rb') as f:
                data = f.read()
            key = self._derive_key(pwd)
            dec = self._xor_data(data, key)
            out = path.replace('.xenc', '') + ".dec"
            with open(out, 'wb') as f:
                f.write(dec)
            QMessageBox.information(self, "Filelock", f"Decrypted -> {out}")
        except Exception as e:
            QMessageBox.critical(self, "Filelock", f"Error: {e}")

class PerformancePanel(GlassFrame):
    def __init__(self, parent: 'GlassDashboard'):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(25,25,25,25)
        layout.setSpacing(15)
        layout.addWidget(SectionHeader("⚡ Performance"))
        
        self.cpu_bar = QProgressBar(); self._style_bar(self.cpu_bar)
        self.ram_bar = QProgressBar(); self._style_bar(self.ram_bar)
        self.disk_bar = QProgressBar(); self._style_bar(self.disk_bar)
        layout.addWidget(QLabel("CPU Usage")); layout.addWidget(self.cpu_bar)
        layout.addWidget(QLabel("Memory Usage")); layout.addWidget(self.ram_bar)
        layout.addWidget(QLabel("Disk Usage (/)")); layout.addWidget(self.disk_bar)
        
        self.setLayout(layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
    
    def _style_bar(self, bar: QProgressBar):
        bar.setStyleSheet("QProgressBar { background: rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); border-radius:8px; color:white; } QProgressBar::chunk { background-color:#64B5F6; border-radius:8px; }")
        bar.setRange(0, 100)
    
    def start_updates(self):
        self.timer.start(1000)
    
    def stop_updates(self):
        self.timer.stop()
    
    def update_stats(self):
        try:
            self.cpu_bar.setValue(int(psutil.cpu_percent()))
            self.ram_bar.setValue(int(psutil.virtual_memory().percent))
            self.disk_bar.setValue(int(psutil.disk_usage('/').percent))
        except Exception:
            pass

class TaskManagerPanel(GlassFrame):
    def __init__(self, parent: 'GlassDashboard'):
        super().__init__(parent)
        layout = QVBoxLayout(); layout.setContentsMargins(25,25,25,25); layout.setSpacing(15)
        layout.addWidget(SectionHeader("📋 Task Manager"))
        
        top = QHBoxLayout()
        refresh = GlassButton("Refresh", "🔄"); refresh.clicked.connect(self.refresh_processes)
        self.end_btn = GlassButton("End Process", "🛑"); self.end_btn.clicked.connect(self.end_selected)
        top.addWidget(refresh); top.addWidget(self.end_btn); top.addStretch()
        layout.addLayout(top)
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["PID", "Name", "CPU %"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QTableWidget { background: rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:12px; color:white; }")
        layout.addWidget(self.table, 1)
        
        self.setLayout(layout)
        self.refresh_processes()
    
    def refresh_processes(self):
        self.table.setRowCount(0)
        try:
            procs = []
            for p in psutil.process_iter(['pid','name','cpu_percent']):
                info = p.info
                procs.append(info)
            procs.sort(key=lambda x: x.get('cpu_percent') or 0, reverse=True)
            for pr in procs[:50]:
                row = self.table.rowCount(); self.table.insertRow(row)
                self.table.setItem(row,0,QTableWidgetItem(str(pr.get('pid'))))
                self.table.setItem(row,1,QTableWidgetItem(str(pr.get('name'))))
                self.table.setItem(row,2,QTableWidgetItem(str(pr.get('cpu_percent') or 0)))
        except Exception:
            pass
    
    def end_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        pid_item = self.table.item(row,0)
        if not pid_item:
            return
        pid = int(pid_item.text())
        confirm = QMessageBox.question(self, "Confirm", f"End process PID {pid}?", QMessageBox.Yes|QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                psutil.Process(pid).terminate()
                self.refresh_processes()
            except Exception as e:
                QMessageBox.critical(self, "Task Manager", f"Error: {e}")

class StoragePanel(GlassFrame):
    def __init__(self, parent: 'GlassDashboard'):
        super().__init__(parent)
        layout = QVBoxLayout(); layout.setContentsMargins(25,25,25,25); layout.setSpacing(15)
        layout.addWidget(SectionHeader("💾 Storage"))
        
        self.partitions_label = QLabel("")
        self.partitions_label.setStyleSheet("color: rgba(255,255,255,0.9);")
        layout.addWidget(self.partitions_label)
        
        scan_row = QHBoxLayout()
        self.scan_path = QLineEdit(); self.scan_path.setPlaceholderText("Path to analyze…")
        browse = GlassButton("Browse", "📂"); browse.clicked.connect(self.browse_folder)
        scan = GlassButton("Scan Large Files", "🔎"); scan.clicked.connect(self.scan_large_files)
        scan_row.addWidget(self.scan_path,1); scan_row.addWidget(browse); scan_row.addWidget(scan)
        layout.addLayout(scan_row)
        
        self.results = QListWidget(); self.results.setStyleSheet("QListWidget { background: rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:12px; color:white; }")
        layout.addWidget(self.results,1)
        
        self.setLayout(layout)
        self.refresh_partitions()
    
    def refresh_partitions(self):
        try:
            parts = psutil.disk_partitions(all=False)
            lines = []
            for p in parts:
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    lines.append(f"{p.device} — {p.mountpoint} — {usage.percent}% used")
                except Exception:
                    continue
            self.partitions_label.setText("\n".join(lines) or "No partitions info available")
        except Exception:
            self.partitions_label.setText("Unable to read partitions")
    
    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder", os.getcwd())
        if path:
            self.scan_path.setText(path)
    
    def scan_large_files(self):
        base = self.scan_path.text().strip() or os.getcwd()
        self.results.clear()
        candidates = []
        try:
            for root, _, files in os.walk(base):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        size = os.path.getsize(fp)
                    except Exception:
                        continue
                    candidates.append((size, fp))
            candidates.sort(reverse=True)
            for size, fp in candidates[:50]:
                self.results.addItem(f"{size/1024/1024:.1f} MB — {fp}")
        except Exception as e:
            QMessageBox.critical(self, "Storage", f"Error: {e}")

class ThemePanel(GlassFrame):
    def __init__(self, parent: 'GlassDashboard'):
        super().__init__(parent)
        self.parent_dashboard = parent
        layout = QVBoxLayout(); layout.setContentsMargins(25,25,25,25); layout.setSpacing(15)
        layout.addWidget(SectionHeader("🎨 Theme"))
        
        self.dark_chk = QCheckBox("Dark Theme")
        self.dark_chk.setChecked(True)
        self.dark_chk.stateChanged.connect(self.apply_theme)
        layout.addWidget(self.dark_chk)
        
        accent_btn = GlassButton("Pick Accent Color", "🎯")
        accent_btn.clicked.connect(self.pick_accent)
        layout.addWidget(accent_btn)
        
        self.preview = QLabel("Preview text")
        self.preview.setStyleSheet("padding:12px; background: rgba(255,255,255,0.08); border-radius:10px;")
        layout.addWidget(self.preview)
        
        save_btn = GlassButton("Save Preferences", "💾")
        save_btn.clicked.connect(self.save_prefs)
        layout.addWidget(save_btn)
        layout.addStretch()
        self.setLayout(layout)
        
        # Load saved
        settings = parent._load_settings()
        accent = settings.get('accent', '#64B5F6')
        self.accent = QColor(accent)
        self.apply_theme()
    
    def pick_accent(self):
        color = QColorDialog.getColor(self.accent, self, "Pick Accent Color")
        if color.isValid():
            self.accent = color
            self.apply_theme()
    
    def apply_theme(self):
        # Currently supports dark only, adjust accent
        accent_hex = self.accent.name()
        self.preview.setStyleSheet(f"padding:12px; background: rgba(255,255,255,0.08); border-radius:10px; border:1px solid {accent_hex};")
        # Could update global stylesheet chunks if desired
    
    def save_prefs(self):
        self.parent_dashboard._save_settings({
            'accent': self.accent.name(),
            'theme': 'dark' if self.dark_chk.isChecked() else 'light'
        })
        QMessageBox.information(self, "Theme", "Preferences saved")

# ----------------------------
# RUN APP
# ----------------------------
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    dashboard = GlassDashboard()
    dashboard.show()
    sys.exit(app.exec_())
