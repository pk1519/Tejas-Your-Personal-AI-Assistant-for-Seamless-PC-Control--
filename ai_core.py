# ai_core.py
import os
import webbrowser
import psutil
import pyautogui
import subprocess
import screen_brightness_control as sbc
from difflib import get_close_matches
from collections import defaultdict
import datetime
import json
import pymongo
import platform
import socket

# ----------------------------
# Offline Voice Recognition
# ----------------------------
import sounddevice as sd
import vosk
import queue

q = queue.Queue()
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

MODEL_PATH = "D:/Projects/TejasAi/vosk-model-small-en-us-0.15"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Please download Vosk model and set MODEL_PATH correctly.")
model = vosk.Model(MODEL_PATH)

def recognize_voice(duration=5):
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        rec = vosk.KaldiRecognizer(model, 16000)
        import time as t
        start = t.time()
        while t.time() - start < duration:
            data = q.get()
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                return res.get("text", "")
        final_res = json.loads(rec.FinalResult())
        return final_res.get("text", "")

# ----------------------------
# MongoDB Notes
# ----------------------------
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["ai_assistant"]
notes_col = db["notes"]

# ----------------------------
# COMMANDS
# ----------------------------
COMMANDS = defaultdict(list)
COMMANDS["volume_up"] = ["volume up", "increase volume", "sound high", "आवाज़ बढ़ा"]
COMMANDS["volume_down"] = ["volume down", "decrease volume", "sound low", "आवाज़ कम"]
COMMANDS["brightness_up"] = ["brightness up", "increase brightness", "bright high", "ब्राइटनेस बढ़ा"]
COMMANDS["brightness_down"] = ["brightness down", "decrease brightness", "dim screen", "ब्राइटनेस कम"]
COMMANDS["open_browser"] = ["open chrome", "launch browser", "start google", "ब्राउज़र खोल"]
COMMANDS["performance_chart"] = ["system performance", "show performance", "ram chart", "cpu chart"]
COMMANDS["take_note"] = ["take note", "remember this", "save note", "नोट लो"]
COMMANDS["youtube"] = ["play youtube", "youtube video", "youtube song", "youtube gaana"]
COMMANDS["search_web"] = ["search", "search for", "google search"]
COMMANDS["wifi"] = ["switch wifi", "change wifi", "connect wifi"]
COMMANDS["bluetooth"] = ["turn on bluetooth", "turn off bluetooth"]
COMMANDS["night_light"] = ["night light on", "night light off"]
COMMANDS["shutdown"] = ["shutdown pc", "turn off pc", "power off"]
COMMANDS["restart"] = ["restart pc", "reboot pc"]
COMMANDS["datetime"] = ["date", "time", "current date", "current time"]
COMMANDS["battery"] = ["battery status", "check battery", "power level"]
COMMANDS["open_app"] = ["open app", "launch app", "start program"]

# ----------------------------
# INTENT DETECTION
# ----------------------------
def detect_intent(user_input):
    user_input = user_input.lower().strip()
    flat_commands = {cmd: intent for intent, phrases in COMMANDS.items() for cmd in phrases}

    # Direct match
    for phrase, intent in flat_commands.items():
        if phrase in user_input:
            return intent

    # Fuzzy match
    closest = get_close_matches(user_input, flat_commands.keys(), n=1, cutoff=0.6)
    if closest:
        return flat_commands[closest[0]]

    return None

# ----------------------------
# ACTIONS
# ----------------------------
def action_volume_up(user_input=""):
    inc = 10
    import re
    match = re.search(r'\d+', user_input)
    if match:
        inc = int(match.group())
    for _ in range(inc//2):
        pyautogui.press("volumeup")
    return f"Volume increased by {inc}%."

def action_volume_down(user_input=""):
    dec = 10
    import re
    match = re.search(r'\d+', user_input)
    if match:
        dec = int(match.group())
    for _ in range(dec//2):
        pyautogui.press("volumedown")
    return f"Volume decreased by {dec}%."

def action_brightness_up(user_input=""):
    inc = 10
    import re
    match = re.search(r'\d+', user_input)
    if match:
        inc = int(match.group())
    try:
        current = sbc.get_brightness(display=0)[0]
        sbc.set_brightness(min(current+inc,100))
        return f"Brightness increased to {min(current+inc,100)}%."
    except Exception as e:
        return f"Brightness error: {e}"

def action_brightness_down(user_input=""):
    dec = 10
    import re
    match = re.search(r'\d+', user_input)
    if match:
        dec = int(match.group())
    try:
        current = sbc.get_brightness(display=0)[0]
        sbc.set_brightness(max(current-dec,0))
        return f"Brightness decreased to {max(current-dec,0)}%."
    except Exception as e:
        return f"Brightness error: {e}"

def action_open_browser(user_input=""):
    webbrowser.open("https://www.google.com")
    return "Browser opened."

def action_performance_chart(user_input=""):
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    processes = [(p.info["name"], p.info["cpu_percent"]) for p in psutil.process_iter(["name","cpu_percent"])]
    high_cpu = sorted(processes, key=lambda x:x[1], reverse=True)[:5]
    report = f"CPU: {cpu}%, RAM: {ram}%, Disk: {disk}%.\nTop CPU processes: {high_cpu}"
    return report

def action_take_note(user_input):
    note = user_input.replace("take note","").strip()
    if note:
        notes_col.insert_one({"note": note, "timestamp": datetime.datetime.now()})
        return "Note saved."
    return "No note content found."

def action_search_web(user_input):
    query = user_input.replace("search","").strip()
    if query:
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searched for {query}."
    return "No search query found."

def action_youtube(user_input):
    query = user_input.replace("youtube","").strip()
    if query:
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return f"Playing {query} on YouTube."
    return "No YouTube query found."

def action_datetime(user_input=""):
    now = datetime.datetime.now()
    return now.strftime("Today is %A, %d %B %Y. Time: %H:%M:%S")

def action_battery(user_input=""):
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        plugged = battery.power_plugged
        return f"Battery at {percent}%. Plugged in: {plugged}."
    return "Battery info unavailable."

def action_shutdown(user_input=""):
    subprocess.call(["shutdown","/s","/t","5"])
    return "Shutting down PC..."

def action_restart(user_input=""):
    subprocess.call(["shutdown","/r","/t","5"])
    return "Restarting PC..."

def action_open_app(user_input):
    app = user_input.replace("open app","").strip()
    if not app: return "Specify app to open."
    try:
        subprocess.Popen(app)
        return f"{app} launched."
    except Exception:
        webbrowser.open(f"https://www.google.com/search?q=download+{app}")
        return f"{app} not found. Redirecting to download page."

# ----------------------------
# LLM FALLBACK
# ----------------------------
def llm_fallback(user_input):
    # Placeholder for GPT/OpenAI fallback
    return f"LLM interpreting: '{user_input}'"

# ----------------------------
# NETWORK INFO
# ----------------------------
def get_network_info():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return {"hostname": hostname, "ip": local_ip}

# ----------------------------
# MAIN HANDLER
# ----------------------------
def handle_task(user_input, llm_fallback_func=None):
    intent = detect_intent(user_input)
    actions = {
        "volume_up": lambda: action_volume_up(user_input),
        "volume_down": lambda: action_volume_down(user_input),
        "brightness_up": lambda: action_brightness_up(user_input),
        "brightness_down": lambda: action_brightness_down(user_input),
        "open_browser": action_open_browser,
        "performance_chart": action_performance_chart,
        "take_note": lambda: action_take_note(user_input),
        "search_web": lambda: action_search_web(user_input),
        "youtube": lambda: action_youtube(user_input),
        "datetime": action_datetime,
        "battery": action_battery,
        "shutdown": action_shutdown,
        "restart": action_restart,
        "open_app": lambda: action_open_app(user_input),
    }
    if intent in actions:
        return actions[intent]()
    elif llm_fallback_func:
        return llm_fallback_func(user_input)
    else:
        return "Command not recognized."
