import sys
import pyttsx3
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPalette, QColor, QFont, QPainter, QPen, QBrush, QLinearGradient, QPixmap, QPainterPath
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout,
    QWidget, QLineEdit, QLabel, QFrame, QGridLayout, QSpacerItem, QSizePolicy, QScrollArea
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
    """Left sidebar for user panel - customizable for future features"""
    
    # Signal for logout
    logout_requested = pyqtSignal()
    
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
        
        # Quick Actions
        quick_actions = self.create_quick_actions()
        layout.addWidget(quick_actions)
        
        # Divider
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.HLine)
        divider2.setStyleSheet("background: rgba(255, 255, 255, 0.1); border: none; height: 1px;")
        layout.addWidget(divider2)
        
        # Settings & Controls
        settings_section = self.create_settings_section()
        layout.addWidget(settings_section)
        
        layout.addStretch()
        
        # Footer
        footer = QLabel("🤖 AI Dashboard v2.0")
        footer.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            font-size: 12px;
            padding: 10px;
            background: transparent;
        """)
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        
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
    
    def create_quick_actions(self):
        section = QWidget()
        section.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        header = QLabel("⚡ Quick Actions")
        header.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            background: transparent;
            padding: 10px 0px;
        """)
        layout.addWidget(header)
        
        # Action buttons - these can be customized for future features
        actions = [
            ("📊", "Analytics"),
            ("🎯", "Goals"),
            ("📈", "Reports"),
            ("⚙️", "Settings"),
            ("🔔", "Notifications"),
            ("🎨", "Customize")
        ]
        
        for icon, text in actions:
            btn = GlassButton(text, icon)
            btn.setFixedHeight(45)
            layout.addWidget(btn)
        
        section.setLayout(layout)
        return section
    
    def create_settings_section(self):
        section = QWidget()
        section.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        header = QLabel("🎛️ Controls")
        header.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            background: transparent;
            padding: 10px 0px;
        """)
        layout.addWidget(header)
        
        # Control buttons
        controls = [
            ("🔊", "Audio Settings"),
            ("🌙", "Theme"),
            ("🔐", "Privacy"),
            ("ℹ️", "Help")
        ]
        
        for icon, text in controls:
            btn = GlassButton(text, icon)
            btn.setFixedHeight(40)
            layout.addWidget(btn)
        
        section.setLayout(layout)
        return section

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
        
        # Voice controls
        voice_layout = QHBoxLayout()
        voice_layout.setSpacing(10)
        
        self.voice_btn = GlassButton("🎤 Voice Input")
        if self.parent_dashboard:
            self.voice_btn.clicked.connect(self.parent_dashboard.on_voice_input)
        self.voice_btn.setFixedHeight(40)
        
        self.speech_toggle = GlassButton("🔊 Voice Output: OFF")
        if self.parent_dashboard:
            self.speech_toggle.clicked.connect(self.parent_dashboard.toggle_speech)
        self.speech_toggle.setFixedHeight(40)
        
        voice_layout.addWidget(self.voice_btn)
        voice_layout.addWidget(self.speech_toggle)
        
        layout.addLayout(input_layout)
        layout.addLayout(voice_layout)
        
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
        
        # Center - Chat Interface  
        self.chat_interface = ChatInterface(self)
        
        # Add to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.chat_interface, 1)  # Chat takes remaining space
        
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
                    stop:0 rgba(20, 20, 40, 0.95),
                    stop:0.3 rgba(40, 20, 60, 0.9),
                    stop:0.7 rgba(60, 40, 80, 0.9),
                    stop:1 rgba(80, 60, 40, 0.95));
            }
            QWidget {
                color: white;
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
    
    def speak(self, text):
        """Convert text to speech"""
        if text and self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Speech error: {e}")

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