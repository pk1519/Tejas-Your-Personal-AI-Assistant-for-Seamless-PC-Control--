import sys, os, threading
import psutil

from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QMessageBox
)

# ---- Optional voice deps (handled gracefully) ----
VOICE_OK = True
try:
    import speech_recognition as sr
except Exception:
    VOICE_OK = False

# ---- Optional global hotkey (Windows needs admin sometimes) ----
HOTKEY_OK = True
try:
    import keyboard  # pip install keyboard
except Exception:
    HOTKEY_OK = False

APP_NAME = "TejasAI"

def human_size(n):
    # bytes -> readable
    for unit in ["B","KB","MB","GB","TB","PB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}EB"

class RobotWidget(QWidget):
    """
    Small frameless robot that peeks in, then sits at the screen edge.
    Clicking it hides the robot and opens the dashboard.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.robot = QLabel(self)
        self.robot.setObjectName("robot")
        self.robot.setStyleSheet("#robot { background: transparent; }")

        # Try PNG first, then JPEG fallback
        img = None
        for name in ("robot.png", "robot.jpeg", "robot.jpg"):
            if os.path.exists(name):
                img = name
                break
        if not img:
            # draw an emoji placeholder if no image file found
            self.robot.setText("🤖")
            self.robot.setStyleSheet("font-size: 96px;")
            self.robot.resize(120, 120)
        else:
            pix = QPixmap(img)
            if pix.isNull():
                self.robot.setText("🤖")
                self.robot.setStyleSheet("font-size: 96px;")
                self.robot.resize(120, 120)
            else:
                pix = pix.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.robot.setPixmap(pix)
                self.robot.resize(pix.width(), pix.height())

        self.resize(self.robot.width(), self.robot.height())

        # Positioning
        screen = QApplication.primaryScreen().availableGeometry()
        self.screen_w = screen.width()
        self.screen_h = screen.height()
        self.margin = 10
        self.y = self.screen_h - self.height() - 60  # near bottom
        self.end_x = self.screen_w - self.width() - self.margin   # fully visible position
        self.peek_x = self.end_x + int(self.width() * 0.45)       # partly outside (peek)
        self.start_x = self.screen_w + 20                          # fully off-screen

        self.move(self.start_x, self.y)

        # Animation
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

        # Click → open dashboard
        self.robot.mousePressEvent = self._on_click

        self._is_visible = False
        self._dashboard = None

    # --- Public API ---
    def run_peek_and_land(self):
        """Peek from edge, wait, then land fully visible."""
        self._is_visible = True
        self.show()
        self._slide(self.start_x, self.y, self.peek_x, self.y, 550)
        QTimer.singleShot(700, lambda: self._slide(self.peek_x, self.y, self.end_x, self.y, 500))

    def summon(self):
        """Summon robot with slide-in if currently hidden."""
        if self._is_visible:
            return
        self.run_peek_and_land()

    def hide_robot(self):
        """Slide robot off-screen and hide the widget."""
        if not self._is_visible:
            return
        def _finish():
            self.hide()
            self._is_visible = False
        self._slide(self.end_x, self.y, self.start_x, self.y, 450, on_done=_finish)

    # --- Internals ---
    def _slide(self, x1, y1, x2, y2, dur, on_done=None):
        self.anim.stop()
        self.anim.setDuration(dur)
        self.anim.setStartValue(QRect(x1, y1, self.width(), self.height()))
        self.anim.setEndValue(QRect(x2, y2, self.width(), self.height()))
        if on_done:
            self.anim.finished.connect(on_done)
            # disconnect after one-shot
            def _cleanup():
                try:
                    self.anim.finished.disconnect(on_done)
                except Exception:
                    pass
            self.anim.finished.connect(_cleanup)
        self.anim.start()

    def _on_click(self, _event):
        """Click robot → hide robot, then show dashboard."""
        self.hide_robot()
        QTimer.singleShot(480, self._open_dashboard)

    def _open_dashboard(self):
        if self._dashboard and self._dashboard.isVisible():
            self._dashboard.raise_()
            self._dashboard.activateWindow()
            return
        self._dashboard = Dashboard(on_close=self._on_dashboard_closed)
        self._dashboard.show()

    def _on_dashboard_closed(self):
        """
        Dashboard closed → do nothing (robot stays hidden) until user uses hotkey.
        """
        pass


class Dashboard(QWidget):
    """
    Glassy dashboard with Text and optional Voice commands.
    Closing this window does NOT bring robot back; you must use the hotkey.
    """
    def __init__(self, on_close=None):
        super().__init__()
        self.on_close = on_close
        self.setWindowTitle(f"{APP_NAME} • Dashboard")
        if os.path.exists("robot.png"):
            self.setWindowIcon(QIcon("robot.png"))

        self.resize(520, 420)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # --- glass / modern style ---
        self.setStyleSheet("""
            QWidget { background-color: rgba(18,18,20, 225); color: #eaeaea; }
            #title { font-size: 20px; font-weight: 600; padding: 4px 0 8px 0; }
            #out {
                background: #111318;
                border: 1px solid #2a2d34;
                border-radius: 12px;
                padding: 10px;
                font-family: Consolas, ui-monospace, SFMono-Regular, Menlo, Monaco, monospace;
                font-size: 13px;
                color: #d7e0ea;
            }
            #in {
                background: #0f1115;
                border: 1px solid #2a2d34;
                border-radius: 10px;
                padding: 10px;
                color: #f2f5f9;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 #2563eb, stop:1 #0ea5e9);
                border: none;
                color: white;
                padding: 10px 14px;
                border-radius: 10px;
                font-weight: 600;
            }
            QPushButton:hover { filter: brightness(1.1); }
            QPushButton:disabled { background: #2b2f36; color: #9aa1aa; }
            #row { margin-top: 8px; }
        """)

        # Layout
        root = QVBoxLayout(self)

        self.title = QLabel("TejasAI Assistant")
        self.title.setObjectName("title")
        self.subtitle = QLabel("Talk or type. Try: battery • cpu • ram • storage")
        root.addWidget(self.title)
        root.addWidget(self.subtitle)

        self.out = QTextEdit()
        self.out.setObjectName("out")
        self.out.setReadOnly(True)
        self.out.setPlaceholderText("Status and replies will appear here…")
        root.addWidget(self.out, 1)

        row = QHBoxLayout()
        row.setObjectName("row")

        self.inp = QLineEdit()
        self.inp.setObjectName("in")
        self.inp.setPlaceholderText("Type a command and press Enter…")
        self.inp.returnPressed.connect(self._handle_text)
        row.addWidget(self.inp, 1)

        self.btn_send = QPushButton("Send")
        self.btn_send.clicked.connect(self._handle_text)
        row.addWidget(self.btn_send)

        self.btn_voice = QPushButton("🎤 Voice")
        self.btn_voice.clicked.connect(self._handle_voice)
        self.btn_voice.setEnabled(VOICE_OK)
        row.addWidget(self.btn_voice)

        root.addLayout(row)

        # hot tips
        self._println("Ready. Try: battery, cpu, ram, storage.  Type 'help' for more.")

    # ---- helpers ----
    def _println(self, text: str):
        self.out.append(text)

    def _handle_text(self):
        cmd = self.inp.text().strip()
        if not cmd:
            return
        self._println(f"> {cmd}")
        self.inp.clear()
        self._process(cmd)

    def _handle_voice(self):
        if not VOICE_OK:
            QMessageBox.warning(self, "Voice Unavailable",
                                "SpeechRecognition/PyAudio not installed or no microphone found.")
            return
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self._println("🎙 Listening…")
            audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            self._println(f"🗣 You: {text}")
            self._process(text)
        except sr.UnknownValueError:
            self._println("❌ Sorry, I couldn't understand.")
        except sr.RequestError:
            self._println("⚠️ Voice service error.")

    def _process(self, raw: str):
        q = raw.lower().strip()

        if q in ("help", "?"):
            self._println(
                "Commands:\n"
                "  battery  → show battery level\n"
                "  cpu      → CPU usage\n"
                "  ram      → memory usage\n"
                "  storage  → disk usage on system drive\n"
                "  clear    → clear screen\n"
                "  close    → close dashboard (robot stays hidden)\n"
            )
            return

        if q == "clear":
            self.out.clear(); return

        if q in ("close", "quit", "exit"):
            self.close(); return

        if "battery" in q:
            b = psutil.sensors_battery()
            if not b:
                self._println("🔋 Battery: not available")
            else:
                state = "🔌 Charging" if b.power_plugged else "🔋 On battery"
                self._println(f"{state} • {int(b.percent)}%")
            return

        if "cpu" in q:
            self._println(f"🖥 CPU: {psutil.cpu_percent(interval=0.4):.0f}%")
            return

        if "ram" in q or "memory" in q:
            m = psutil.virtual_memory()
            self._println(f"💾 RAM: {m.percent:.0f}%  ({human_size(m.used)} / {human_size(m.total)})")
            return

        if "storage" in q or "disk" in q:
            # system drive
            drive = os.getenv("SystemDrive", "/")
            try:
                import shutil
                total, used, free = shutil.disk_usage(drive)
                self._println(
                    f"📦 Storage {drive}: used {human_size(used)} / {human_size(total)} "
                    f"({used/total*100:.0f}%), free {human_size(free)}"
                )
            except Exception as e:
                self._println(f"📦 Storage: error • {e}")
            return

        self._println("🤷 Unknown command. Type 'help' to see options.")

    def closeEvent(self, event):
        # Don’t bring robot back; leave hidden until hotkey.
        if callable(self.on_close):
            try:
                self.on_close()
            except Exception:
                pass
        event.accept()


def main():
    app = QApplication(sys.argv)

    robot = RobotWidget()
    robot.run_peek_and_land()  # initial peek + land

    # Global hotkey: summon robot only (no toggle). If already visible, ignore.
    if HOTKEY_OK:
        keyboard.add_hotkey("ctrl+shift+t", lambda: robot.summon())

        # keep keyboard hook alive in a daemon thread (Windows quirk on some setups)
        def _hotkey_pump():
            keyboard.wait()
        th = threading.Thread(target=_hotkey_pump, daemon=True)
        th.start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
