import sys
from PyQt5.QtWidgets import QApplication
from robot_overlay import RobotOverlay
from dashboard import GlassDashboard
from ai_core import AICore  # Added AI core import

def show_dashboard_near_robot(robot: RobotOverlay, dashboard: GlassDashboard):
    """Position dashboard near robot overlay"""
    r = robot.geometry()
    screen = QApplication.primaryScreen().availableGeometry()
    # Calculate preferred position
    preferred_x = r.x() - dashboard.width() - 12
    if preferred_x < screen.x():
        preferred_x = r.x() + r.width() + 12
    preferred_y = r.y() + (r.height() - dashboard.height()) // 2
    # Ensure dashboard stays within screen bounds
    preferred_x = max(screen.x(), min(preferred_x, screen.x() + screen.width() - dashboard.width()))
    preferred_y = max(screen.y(), min(preferred_y, screen.y() + screen.height() - dashboard.height()))
    # Position and show dashboard
    dashboard.move(preferred_x, preferred_y)
    dashboard.show()
    dashboard.raise_()
    dashboard.activateWindow()

def handle_robot_click(robot: RobotOverlay, dashboard: GlassDashboard):
    """Handle robot click - show auth dialog if needed, then dashboard"""
    if not dashboard.auth_manager.is_user_authenticated():
        print("🔐 User not authenticated, showing auth dialog...")
        dashboard.show_auth_dialog()
        # Dashboard will be shown automatically after successful authentication
        # via the login_successful signal connection in GlassDashboard.__init__
    else:
        print(f"✅ User already authenticated: {dashboard.auth_manager.get_user_info().get('name')}")
        show_dashboard_near_robot(robot, dashboard)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Set application style
    app.setStyle('Fusion')
    # Create robot overlay and dashboard
    robot = RobotOverlay()
    dashboard = GlassDashboard()
    # (Optional/Example) Create an AICore object if required
    ai_core = AICore()
    # Connect robot click to authentication flow
    robot.showDashboard.connect(lambda: handle_robot_click(robot, dashboard))
    # Connect successful login to show dashboard
    dashboard.auth_manager.login_successful.connect(
        lambda user_data: show_dashboard_near_robot(robot, dashboard)
    )
    # Show robot widget on screen
    robot.show()
    print("🚀 AI Dashboard started successfully!")
    print("🤖 Click the robot overlay to begin authentication")
    # Start the application event loop
    sys.exit(app.exec_())
