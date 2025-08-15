# dashboard.py
import sys
import pyttsx3
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QTextEdit, QVBoxLayout,
    QWidget, QLineEdit
)
from ai_core import handle_task, llm_fallback, recognize_voice, get_network_info

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glass Dashboard with AI")
        self.setGeometry(200, 200, 600, 450)

        self.enable_speech_output = False
        self.tts_engine = pyttsx3.init()

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(self._glass_style())

        # Text input
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your command here and press Enter...")
        self.text_input.returnPressed.connect(self.on_text_submit)
        self.text_input.setStyleSheet(self._glass_style())

        # Voice button
        self.listen_button = QPushButton("🎤 Speak Command")
        self.listen_button.clicked.connect(self.on_voice_button_click)
        self.listen_button.setStyleSheet(self._button_style())

        # Speech toggle
        self.speak_toggle_button = QPushButton("🔊 Enable Speech Output")
        self.speak_toggle_button.clicked.connect(self.toggle_speech_output)
        self.speak_toggle_button.setStyleSheet(self._button_style())

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.chat_display)
        layout.addWidget(self.text_input)
        layout.addWidget(self.listen_button)
        layout.addWidget(self.speak_toggle_button)

        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet(self._window_style())
        self.setCentralWidget(container)

        self._apply_dark_theme()

    def toggle_speech_output(self):
        self.enable_speech_output = not self.enable_speech_output
        status = "enabled" if self.enable_speech_output else "disabled"
        self.chat_display.append(f"🔄 Speech output {status}.")
        self.speak_toggle_button.setText(
            "🔊 Disable Speech Output" if self.enable_speech_output else "🔊 Enable Speech Output"
        )

    def speak(self, text):
        if self.enable_speech_output and text:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

    def on_voice_button_click(self):
        self.chat_display.append("🎤 Listening...")
        self.repaint()
        voice_text = recognize_voice(duration=5)
        if voice_text:
            self.chat_display.append(f"🗣 You said: {voice_text}")
            ai_reply = handle_task(voice_text, llm_fallback_func=llm_fallback)
            self.chat_display.append(f"🤖 {ai_reply}")
            self.speak(ai_reply)

    def on_text_submit(self):
        user_text = self.text_input.text().strip()
        if user_text:
            self.chat_display.append(f"🗣 {user_text}")
            ai_reply = handle_task(user_text, llm_fallback_func=llm_fallback)
            self.chat_display.append(f"🤖 {ai_reply}")
            self.speak(ai_reply)
            self.text_input.clear()

    # ----------------------------
    # STYLES
    # ----------------------------
    def _apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def _glass_style(self):
        return """
        background-color: rgba(255, 255, 255, 0.08);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 5px;
        """

    def _button_style(self):
        return """
        QPushButton {
            background-color: rgba(255, 255, 255, 0.15);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.25);
        }
        """

    def _window_style(self):
        return "background-color: rgba(20, 20, 20, 0.85);"

# ----------------------------
# RUN APP
# ----------------------------
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())
