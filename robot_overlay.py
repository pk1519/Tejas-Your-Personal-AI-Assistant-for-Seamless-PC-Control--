# robot_overlay.py
from PyQt5.QtWidgets import QWidget, QLabel, QShortcut, QApplication
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, pyqtSignal
from PyQt5.QtGui import QFont, QKeySequence

# Optional global hotkey support (install `keyboard` if you want system-wide hotkey)
try:
    import keyboard
    KEYBOARD_OK = True
except Exception:
    KEYBOARD_OK = False


class RobotOverlay(QWidget):
    """Floating robot overlay that peeks/hides and emits showDashboard when clicked while static."""
    showDashboard = pyqtSignal()

    def __init__(self, margin=12):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Robot glyph
        self.label = QLabel("🤖", self)
        self.label.setFont(QFont("Segoe UI Emoji", 48))
        self.label.adjustSize()
        self.resize(self.label.size())

        self.margin = margin
        self.is_static = False     # True while waiting and clickable
        self._running = False      # prevents overlapping sequences
        self._pending_callback = None
        self.anim = None

        # compute screen bottom-right placement
        screen = QApplication.primaryScreen().availableGeometry()
        sx, sy, sw, sh = screen.x(), screen.y(), screen.width(), screen.height()
        self.start_x = sx + sw + 20                          # fully off-screen
        self.end_x = sx + sw - self.width() - self.margin    # visible position slightly inset
        self.y = sy + sh - self.height() - 60                # near bottom

        self.move(self.start_x, self.y)

        # Shortcut inside application
        self.shortcut = QShortcut(QKeySequence("Ctrl+7"), self)
        self.shortcut.setContext(Qt.ApplicationShortcut)
        self.shortcut.activated.connect(self.start_sequence)

        # optional global hotkey (requires keyboard lib)
        if KEYBOARD_OK:
            try:
                # schedule call into the Qt main thread
                keyboard.add_hotkey("ctrl+7", lambda: QTimer.singleShot(0, self.start_sequence))
            except Exception:
                pass

        # Start the initial sequence shortly after launch
        QTimer.singleShot(400, self.start_sequence)

    # ---------------------------
    # Public API
    # ---------------------------
    def start_sequence(self):
        """Start the two-peek sequence (1st peek 2s, hide 1s, 2nd peek 5s, hide)."""
        if self._running:
            return
        self._running = True
        self.show()
        # first peek → wait 2s → hide
        self._animate_in(lambda: QTimer.singleShot(2000, self._first_hide))

    # ---------------------------
    # Animation steps
    # ---------------------------
    def _first_hide(self):
        self._animate_out(lambda: QTimer.singleShot(1000, self._second_peek))

    def _second_peek(self):
        self._animate_in(lambda: QTimer.singleShot(5000, self._second_hide))

    def _second_hide(self):
        self._animate_out(self._finish_sequence)

    def _finish_sequence(self):
        self.is_static = False
        self.hide()
        self._running = False

    # ---------------------------
    # Animation helpers
    # ---------------------------
    def _animate_in(self, on_finished=None, duration=420):
        """Slide in to end_x; when finished set clickable and call on_finished after waiting period."""
        def _post():
            # become static/clickable while waiting period runs (on_finished will be scheduled by caller)
            self.is_static = True
            if callable(on_finished):
                on_finished()

        self._animate_to(QPoint(self.end_x, self.y), _post, duration)

    def _animate_out(self, on_finished=None, duration=380):
        """Slide out to start_x and mark not-static."""
        def _post():
            self.is_static = False
            if callable(on_finished):
                on_finished()
        self._animate_to(QPoint(self.start_x, self.y), _post, duration)

    def _animate_to(self, end_pos, on_finished=None, duration=400):
        # stop previous animation and connect a single-shot finished handler
        if self.anim:
            try:
                self.anim.stop()
            except Exception:
                pass

        self._pending_callback = on_finished
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(duration)
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(end_pos)
        self.anim.finished.connect(self._on_anim_finished)
        self.anim.start()

    def _on_anim_finished(self):
        # disconnect and call pending callback exactly once
        try:
            self.anim.finished.disconnect(self._on_anim_finished)
        except Exception:
            pass
        cb = self._pending_callback
        self._pending_callback = None
        if callable(cb):
            cb()

    # ---------------------------
    # Mouse handling
    # ---------------------------
    def mousePressEvent(self, event):
        # Only respond when in static/waiting state and click inside the glyph bounds
        if not self.is_static:
            return
        if event.button() == Qt.LeftButton:
            if self.label.geometry().contains(event.pos()):
                # Emit signal to show the dashboard (main will listen and show it)
                self.showDashboard.emit()

    # If you want to explicitly free a global hotkey when closing:
    def cleanup(self):
        if KEYBOARD_OK:
            try:
                keyboard.clear_all_hotkeys()
            except Exception:
                pass
