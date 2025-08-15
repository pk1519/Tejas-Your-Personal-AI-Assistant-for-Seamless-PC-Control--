# tasks.py
import os

def clear_cache():
    os.system("del /q/f/s %TEMP%\\*")  # Windows clear temp folder
    return "🧹 Cache cleared successfully."

def increase_volume():
    return "🔊 Volume increased."

def decrease_volume():
    return "🔉 Volume decreased."

def open_browser():
    os.system("start chrome")  # Open Chrome
    return "🌐 Browser opened."

ACTIONS = {
    "clear_cache": clear_cache,
    "increase_volume": increase_volume,
    "decrease_volume": decrease_volume,
    "open_browser": open_browser
}

def execute_task(action):
    if action in ACTIONS:
        return ACTIONS[action]()
    else:
        return "❓ Unknown action."
