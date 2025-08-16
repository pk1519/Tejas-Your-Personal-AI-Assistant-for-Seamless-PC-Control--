# test_auth.py - Test the authentication system
import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from auth_manager import AuthManager
from auth_dialog import AuthDialog

class AuthTester(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 Authentication Tester")
        self.setFixedSize(400, 300)
        
        # Initialize auth manager
        self.auth_manager = AuthManager()
        self.auth_dialog = None
        
        # Setup UI
        self.setup_ui()
        
        # Connect signals
        self.auth_manager.login_successful.connect(self.on_login_success)
        self.auth_manager.logout_successful.connect(self.on_logout_success)
        
        # Check initial auth state
        self.update_status()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel("🔄 Checking authentication status...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; padding: 10px;")
        
        self.user_info_label = QLabel("")
        self.user_info_label.setAlignment(Qt.AlignCenter)
        self.user_info_label.setStyleSheet("font-size: 12px; color: gray; padding: 5px;")
        
        self.login_btn = QPushButton("🔐 Login with Google")
        self.login_btn.clicked.connect(self.show_auth_dialog)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: #4285f4;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #3367d6;
            }
        """)
        
        self.logout_btn = QPushButton("🚪 Logout")
        self.logout_btn.clicked.connect(self.auth_manager.logout)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background: #ea4335;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #d93025;
            }
        """)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.user_info_label)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.logout_btn)
        
        self.setLayout(layout)
        self.setStyleSheet("background: white;")
    
    def update_status(self):
        if self.auth_manager.is_user_authenticated():
            user = self.auth_manager.get_user_info()
            self.status_label.setText("✅ Authenticated")
            self.status_label.setStyleSheet("color: green; font-size: 14px; padding: 10px;")
            self.user_info_label.setText(f"Welcome, {user.get('name', 'User')}!\n{user.get('email', '')}")
            self.login_btn.setVisible(False)
            self.logout_btn.setVisible(True)
        else:
            self.status_label.setText("❌ Not Authenticated")
            self.status_label.setStyleSheet("color: red; font-size: 14px; padding: 10px;")
            self.user_info_label.setText("Please login to continue")
            self.login_btn.setVisible(True)
            self.logout_btn.setVisible(False)
    
    def show_auth_dialog(self):
        if not self.auth_dialog:
            self.auth_dialog = AuthDialog(self)
            self.auth_dialog.google_auth_requested.connect(self.handle_google_auth)
        
        self.auth_dialog.hide_loading()
        self.auth_dialog.exec_()
    
    def handle_google_auth(self):
        if self.auth_dialog:
            self.auth_dialog.show_loading()
        
        # Start authentication
        self.auth_manager.initiate_google_auth()
        
        # Close dialog
        if self.auth_dialog:
            self.auth_dialog.accept()
    
    def on_login_success(self, user_data):
        print(f"🎉 Login successful: {user_data}")
        self.update_status()
    
    def on_logout_success(self):
        print("👋 Logout successful")
        self.update_status()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    tester = AuthTester()
    tester.show()
    
    sys.exit(app.exec_())