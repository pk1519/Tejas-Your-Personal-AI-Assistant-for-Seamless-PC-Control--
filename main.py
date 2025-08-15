# main.py
import sys
from PyQt5.QtWidgets import QApplication
from robot_overlay import RobotOverlay
from dashboard import Dashboard
from PyQt5.QtCore import QTimer

def show_dashboard_near_robot(robot: RobotOverlay, dashboard: Dashboard):
    # Position dashboard to the left of robot if possible, otherwise right
    r = robot.geometry()
    screen = QApplication.primaryScreen().availableGeometry()
    preferred_x = r.x() - dashboard.width() - 12
    if preferred_x < screen.x():
        preferred_x = r.x() + r.width() + 12
    preferred_y = r.y() + (r.height() - dashboard.height()) // 2

    # clamp inside screen
    preferred_x = max(screen.x(), min(preferred_x, screen.x() + screen.width() - dashboard.width()))
    preferred_y = max(screen.y(), min(preferred_y, screen.y() + screen.height() - dashboard.height()))

    dashboard.move(preferred_x, preferred_y)
    dashboard.show()
    dashboard.raise_()
    dashboard.activateWindow()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    robot = RobotOverlay()
    dashboard = Dashboard()

    # connect the signal
    robot.showDashboard.connect(lambda: show_dashboard_near_robot(robot, dashboard))

    # Keep small safety: if you want the app to quit when dashboard closes, you can connect signals.
    # Example: dashboard.closeEvent override or add qApp.quit() on a 'Quit' button.

    # show robot widget (initial sequence will start on its own)
    robot.show()

    sys.exit(app.exec_())
