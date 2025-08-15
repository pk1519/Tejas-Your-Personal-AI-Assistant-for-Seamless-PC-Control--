# Tejas AI – Desktop Assistant

**Tejas AI** is a smart desktop assistant built for Windows PCs, combining offline voice recognition, natural language understanding, and system automation. It allows users to control system settings, launch apps, search the web, manage notes, and perform various tasks using voice or text commands, all through a sleek glass-style dashboard interface.

---

## Features

### 1. Voice & Text Commands
- Real-time voice recognition using **Vosk** for offline processing.
- Text input for typing commands.
- Smart fallback to **LLM** for free-form or unrecognized commands.
- Speech output for AI responses using **pyttsx3**.

### 2. System Controls
- Adjust **volume** and **brightness** (incremental or custom values).
- View detailed **CPU and RAM stats**.
- Switch between **WiFi networks** and manage **Bluetooth**.
- Enable or disable **Night Light**.
- Shutdown or restart your PC.

### 3. Application & Browser Automation
- Open installed applications; if not found, redirect to download page.
- Search the web or YouTube directly from the assistant.
- Play YouTube songs or videos.

### 4. Notes & Reminders
- Save notes to **MongoDB** for persistent storage.
- Retrieve previously saved notes.

### 5. Smart AI Assistance
- **LLM-based fallback** for natural language understanding.
- Understands flexible queries with varied spelling, grammar, or phrasing.
- Can interpret complex instructions like "increase volume by 40%" or "switch to LongLasting WiFi".

### 6. UI & Experience
- Glass-style, semi-transparent **PyQt5 dashboard**.
- Toggle speech output on/off.
- Live chat display with AI responses and user input.

---


