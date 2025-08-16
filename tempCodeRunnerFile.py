import sys
from PyQt5.QtWidgets import QApplication
from robot_overlay import RobotOverlay
from dashboard import GlassDashboard  # Correct import

from PyQt5.QtCore import QTimer
from ai_core import handle_task, llm_fallback

def show_dashboard_near_robot(robot: RobotOverlay, dashboard: GlassDashboard):  # Update type hint
    r = robot.geometry()
    screen = QApplication.primaryScreen().availableGeometry()
    preferred_x = r.x() - dashboard.width() - 12
    if preferred_x < screen.x():
        preferred_x = r.x() + r.width() + 12
    preferred_y = r.y() + (r.height() - dashboard.height()) // 2
    preferred_x = max(screen.x(), min(preferred_x, screen.x() + screen.width() - dashboard.width()))
    preferred_y = max(screen.y(), min(preferred_y, screen.y() + screen.height() - dashboard.height()))
    dashboard.move(preferred_x, preferred_y)
    dashboard.show()
    dashboard.raise_()
    dashboard.activateWindow()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    robot = RobotOverlay()
    dashboard = GlassDashboard()  # Instantiate the correct class

    # Connect robot click to open dashboard
    robot.showDashboard.connect(lambda: show_dashboard_near_robot(robot, dashboard))

    # Show robot widget
    robot.show()
    sys.exit(app.exec_())
