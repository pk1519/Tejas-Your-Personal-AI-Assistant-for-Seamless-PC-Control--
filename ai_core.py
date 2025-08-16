import os
import sys
import subprocess
import webbrowser
import platform
import json
import re
import time
import psutil
import threading
from pathlib import Path
from datetime import datetime
import requests
if platform.system() == "Windows":
    import winreg
import shutil

class AICore:
    def __init__(self):
        self.system = platform.system()
        self.conversations_history = []
        self.app_database = self._build_app_database()
        self.common_tasks = self._load_common_tasks()
        
    def _build_app_database(self):
        """Build a database of common applications and their download URLs"""
        return {
            # Development Tools
            'vscode': {
                'names': ['visual studio code', 'vs code', 'vscode', 'code'],
                'executable': 'Code.exe' if self.system == 'Windows' else 'code',
                'download_url': 'https://code.visualstudio.com/download',
                'description': 'Code Editor'
            },
            'pycharm': {
                'names': ['pycharm', 'py charm'],
                'executable': 'pycharm64.exe' if self.system == 'Windows' else 'pycharm',
                'download_url': 'https://www.jetbrains.com/pycharm/download/',
                'description': 'Python IDE'
            },
            'sublime': {
                'names': ['sublime text', 'sublime'],
                'executable': 'sublime_text.exe' if self.system == 'Windows' else 'subl',
                'download_url': 'https://www.sublimetext.com/download',
                'description': 'Text Editor'
            },
            'atom': {
                'names': ['atom', 'atom editor'],
                'executable': 'atom.exe' if self.system == 'Windows' else 'atom',
                'download_url': 'https://github.com/atom/atom/releases',
                'description': 'Text Editor'
            },
            'git': {
                'names': ['git', 'git bash'],
                'executable': 'git.exe' if self.system == 'Windows' else 'git',
                'download_url': 'https://git-scm.com/downloads',
                'description': 'Version Control'
            },
            
            # Browsers
            'chrome': {
                'names': ['chrome', 'google chrome'],
                'executable': 'chrome.exe' if self.system == 'Windows' else 'google-chrome',
                'download_url': 'https://www.google.com/chrome/',
                'description': 'Web Browser'
            },
            'firefox': {
                'names': ['firefox', 'mozilla firefox'],
                'executable': 'firefox.exe' if self.system == 'Windows' else 'firefox',
                'download_url': 'https://www.mozilla.org/firefox/download/',
                'description': 'Web Browser'
            },
            'edge': {
                'names': ['edge', 'microsoft edge'],
                'executable': 'msedge.exe' if self.system == 'Windows' else 'microsoft-edge',
                'download_url': 'https://www.microsoft.com/edge/download',
                'description': 'Web Browser'
            },
            
            # Media & Design
            'vlc': {
                'names': ['vlc', 'vlc player', 'vlc media player'],
                'executable': 'vlc.exe' if self.system == 'Windows' else 'vlc',
                'download_url': 'https://www.videolan.org/vlc/download-windows.html',
                'description': 'Media Player'
            },
            'photoshop': {
                'names': ['photoshop', 'adobe photoshop', 'ps'],
                'executable': 'Photoshop.exe' if self.system == 'Windows' else 'photoshop',
                'download_url': 'https://www.adobe.com/products/photoshop.html',
                'description': 'Photo Editor'
            },
            'gimp': {
                'names': ['gimp'],
                'executable': 'gimp.exe' if self.system == 'Windows' else 'gimp',
                'download_url': 'https://www.gimp.org/downloads/',
                'description': 'Photo Editor'
            },
            'obs': {
                'names': ['obs', 'obs studio'],
                'executable': 'obs64.exe' if self.system == 'Windows' else 'obs',
                'download_url': 'https://obsproject.com/download',
                'description': 'Screen Recorder'
            },
            
            # Communication
            'discord': {
                'names': ['discord'],
                'executable': 'Discord.exe' if self.system == 'Windows' else 'discord',
                'download_url': 'https://discord.com/download',
                'description': 'Communication'
            },
            'slack': {
                'names': ['slack'],
                'executable': 'slack.exe' if self.system == 'Windows' else 'slack',
                'download_url': 'https://slack.com/downloads',
                'description': 'Team Communication'
            },
            'zoom': {
                'names': ['zoom'],
                'executable': 'Zoom.exe' if self.system == 'Windows' else 'zoom',
                'download_url': 'https://zoom.us/download',
                'description': 'Video Conferencing'
            },
            'whatsapp': {
                'names': ['whatsapp', 'whatsapp desktop'],
                'executable': 'WhatsApp.exe' if self.system == 'Windows' else 'whatsapp-desktop',
                'download_url': 'https://www.whatsapp.com/download',
                'description': 'Messaging'
            },
            
            # Office & Productivity
            'word': {
                'names': ['word', 'microsoft word', 'ms word'],
                'executable': 'WINWORD.EXE' if self.system == 'Windows' else 'libreoffice',
                'download_url': 'https://www.microsoft.com/microsoft-365',
                'description': 'Word Processor'
            },
            'excel': {
                'names': ['excel', 'microsoft excel', 'ms excel'],
                'executable': 'EXCEL.EXE' if self.system == 'Windows' else 'libreoffice',
                'download_url': 'https://www.microsoft.com/microsoft-365',
                'description': 'Spreadsheet'
            },
            'powerpoint': {
                'names': ['powerpoint', 'microsoft powerpoint', 'ppt'],
                'executable': 'POWERPNT.EXE' if self.system == 'Windows' else 'libreoffice',
                'download_url': 'https://www.microsoft.com/microsoft-365',
                'description': 'Presentation'
            },
            'notion': {
                'names': ['notion'],
                'executable': 'Notion.exe' if self.system == 'Windows' else 'notion-app',
                'download_url': 'https://www.notion.so/desktop',
                'description': 'Note Taking'
            },
            
            # System Tools
            'cmd': {
                'names': ['command prompt', 'cmd', 'terminal'],
                'executable': 'cmd.exe' if self.system == 'Windows' else 'gnome-terminal',
                'download_url': None,  # Built-in
                'description': 'Command Line'
            },
            'powershell': {
                'names': ['powershell', 'windows powershell'],
                'executable': 'powershell.exe' if self.system == 'Windows' else None,
                'download_url': 'https://github.com/PowerShell/PowerShell/releases',
                'description': 'Command Line'
            },
            'notepad': {
                'names': ['notepad'],
                'executable': 'notepad.exe' if self.system == 'Windows' else 'gedit',
                'download_url': None,  # Built-in
                'description': 'Text Editor'
            },
            'calculator': {
                'names': ['calculator', 'calc'],
                'executable': 'calc.exe' if self.system == 'Windows' else 'gnome-calculator',
                'download_url': None,  # Built-in
                'description': 'Calculator'
            },
            
            # Gaming
            'steam': {
                'names': ['steam'],
                'executable': 'steam.exe' if self.system == 'Windows' else 'steam',
                'download_url': 'https://store.steampowered.com/about/',
                'description': 'Gaming Platform'
            },
            'epicgames': {
                'names': ['epic games', 'epic games launcher'],
                'executable': 'EpicGamesLauncher.exe' if self.system == 'Windows' else 'epic-games-launcher',
                'download_url': 'https://www.epicgames.com/store/download',
                'description': 'Gaming Platform'
            }
        }

    # File Management Methods
    def list_files(self, path=None):
        """List files in directory"""
        try:
            if path is None:
                path = os.getcwd()
            
            files = os.listdir(path)
            result = f"📁 **Files in {path}:**\n"
            
            folders = [f for f in files if os.path.isdir(os.path.join(path, f))]
            files_only = [f for f in files if os.path.isfile(os.path.join(path, f))]
            
            for folder in sorted(folders):
                result += f"📂 {folder}/\n"
            
            for file in sorted(files_only):
                size = os.path.getsize(os.path.join(path, file))
                result += f"📄 {file} ({self._bytes_to_readable(size)})\n"
            
            return result
        except Exception as e:
            return f"❌ Unable to list files: {str(e)}"
    
    def create_folder(self, folder_name):
        """Create a new folder"""
        try:
            if not folder_name:
                return "❌ Please specify a folder name"
            
            os.makedirs(folder_name, exist_ok=True)
            return f"✅ Folder '{folder_name}' created successfully"
        except Exception as e:
            return f"❌ Unable to create folder: {str(e)}"
    
    def delete_file(self, file_path):
        """Delete a file or folder"""
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                return f"✅ File '{file_path}' deleted successfully"
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                return f"✅ Folder '{file_path}' deleted successfully"
            else:
                return f"❌ File or folder '{file_path}' not found"
        except Exception as e:
            return f"❌ Unable to delete: {str(e)}"
    
    def copy_file(self, source, destination):
        """Copy a file"""
        try:
            if os.path.isfile(source):
                shutil.copy2(source, destination)
                return f"✅ File copied from '{source}' to '{destination}'"
            elif os.path.isdir(source):
                shutil.copytree(source, destination)
                return f"✅ Folder copied from '{source}' to '{destination}'"
            else:
                return f"❌ Source '{source}' not found"
        except Exception as e:
            return f"❌ Unable to copy: {str(e)}"
    
    def move_file(self, source, destination):
        """Move a file"""
        try:
            shutil.move(source, destination)
            return f"✅ Moved '{source}' to '{destination}'"
        except Exception as e:
            return f"❌ Unable to move: {str(e)}"
    
    def search_files(self, pattern, path=None):
        """Search for files matching pattern"""
        try:
            if path is None:
                path = os.getcwd()
            
            matches = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if pattern.lower() in file.lower():
                        matches.append(os.path.join(root, file))
            
            if matches:
                result = f"🔍 **Found {len(matches)} files matching '{pattern}':**\n"
                for match in matches[:20]:  # Limit to 20 results
                    result += f"📄 {match}\n"
                if len(matches) > 20:
                    result += f"... and {len(matches) - 20} more files\n"
                return result
            else:
                return f"❌ No files found matching '{pattern}'"
        except Exception as e:
            return f"❌ Unable to search files: {str(e)}"
    
    def take_screenshot(self):
        """Take a screenshot"""
        try:
            from PIL import ImageGrab
            import datetime
            
            # Create screenshots folder if it doesn't exist
            screenshots_dir = os.path.join(os.path.expanduser("~"), "Screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)
            
            # Take screenshot
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            return f"📸 Screenshot saved to: {filepath}"
        except ImportError:
            return "❌ PIL (Pillow) library required for screenshots. Install with: pip install Pillow"
        except Exception as e:
            return f"❌ Unable to take screenshot: {str(e)}"
    
    # Web and Search Methods
    def open_website(self, url):
        """Open a website"""
        try:
            if not url:
                return "❌ Please specify a URL"
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            return f"🌐 Opening {url} in your default browser"
        except Exception as e:
            return f"❌ Unable to open website: {str(e)}"
    
    def google_search(self, query):
        """Perform a Google search"""
        try:
            if not query:
                return "❌ Please specify what to search for"
            
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"🔍 Searching Google for: {query}"
        except Exception as e:
            return f"❌ Unable to perform search: {str(e)}"
    
    # Time and Date Methods
    def get_current_time(self):
        """Get current time"""
        try:
            current_time = datetime.now().strftime("%I:%M:%S %p")
            return f"🕐 Current time: {current_time}"
        except Exception as e:
            return f"❌ Unable to get time: {str(e)}"
    
    def get_current_date(self):
        """Get current date"""
        try:
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            return f"📅 Current date: {current_date}"
        except Exception as e:
            return f"❌ Unable to get date: {str(e)}"
    
    # Weather Method
    
    def _load_common_tasks(self):
        """Load common computer tasks and their implementations"""
        return {
            'system_info': self.get_system_info,
            'battery_status': self.get_battery_status,
            'running_processes': self.get_running_processes,
            'network_info': self.get_network_info,
            'disk_usage': self.get_disk_usage,
            'memory_usage': self.get_memory_usage,
            'shutdown': self.shutdown_system,
            'restart': self.restart_system,
            'sleep': self.sleep_system,
            'lock': self.lock_system,
            'volume_up': self.volume_up,
            'volume_down': self.volume_down,
            'mute': self.mute_volume,
            'unmute': self.unmute_volume,
            'screenshot': self.take_screenshot,
            'list_files': self.list_files,
            'create_folder': self.create_folder,
            'delete_file': self.delete_file,
            'copy_file': self.copy_file,
            'move_file': self.move_file,
            'search_files': self.search_files,
            'get_weather': self.get_weather,
            'get_time': self.get_current_time,
            'get_date': self.get_current_date,
            'open_website': self.open_website,
            'google_search': self.google_search
        }
    
    def process_command(self, user_input):
        """Main method to process user commands"""
        try:
            user_input = user_input.lower().strip()
            
            # Store conversation
            self.conversations_history.append({
                'user': user_input,
                'timestamp': datetime.now().isoformat(),
                'response': None
            })
            
            response = ""
            
            # Check for application opening requests
            if any(keyword in user_input for keyword in ['open', 'launch', 'start', 'run']):
                response = self._handle_app_request(user_input)
            
            # Check for system tasks
            elif any(keyword in user_input for keyword in ['shutdown', 'restart', 'sleep', 'lock']):
                response = self._handle_system_control(user_input)
            
            # Check for file operations
            elif any(keyword in user_input for keyword in ['file', 'folder', 'directory', 'create', 'delete', 'copy', 'move']):
                response = self._handle_file_operations(user_input)
            
            # Check for system information
            elif any(keyword in user_input for keyword in ['battery', 'memory', 'disk', 'system', 'process', 'network']):
                response = self._handle_system_info(user_input)
            
            # Check for volume control
            elif any(keyword in user_input for keyword in ['volume', 'sound', 'mute', 'unmute']):
                response = self._handle_volume_control(user_input)
            
            # Check for web-related tasks
            elif any(keyword in user_input for keyword in ['search', 'google', 'website', 'browse']):
                response = self._handle_web_tasks(user_input)
            
            # Check for time/date requests
            elif any(keyword in user_input for keyword in ['time', 'date', 'clock']):
                response = self._handle_time_date(user_input)
            
            # Check for weather requests
            elif 'weather' in user_input:
                response = self._handle_weather(user_input)
            
            # Check for screenshot
            elif 'screenshot' in user_input:
                response = self.take_screenshot()
            
            # Basic conversational responses
            else:
                response = self._handle_conversation(user_input)
            
            # Store response
            self.conversations_history[-1]['response'] = response
            return response
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _handle_app_request(self, user_input):
        """Handle application opening requests"""
        # Extract app name from user input
        app_name = self._extract_app_name(user_input)
        
        if app_name:
            # Check if app exists in our database
            app_info = None
            for app_key, app_data in self.app_database.items():
                if any(name in user_input for name in app_data['names']):
                    app_info = app_data
                    break
            
            if app_info:
                # Try to open the application
                if self._open_application(app_info):
                    return f"✅ Opening {app_info['description']}..."
                else:
                    if app_info['download_url']:
                        webbrowser.open(app_info['download_url'])
                        return f"❌ {app_info['description']} not found on your system. Opening download page..."
                    else:
                        return f"❌ {app_info['description']} not found on your system."
            else:
                return f"🤔 I'm not familiar with '{app_name}'. Can you be more specific?"
        else:
            return "🤔 Which application would you like me to open?"
    
    def _extract_app_name(self, user_input):
        """Extract application name from user input"""
        # Remove common command words
        words_to_remove = ['open', 'launch', 'start', 'run', 'please', 'can', 'you', 'the', 'app', 'application']
        words = user_input.split()
        filtered_words = [word for word in words if word not in words_to_remove]
        return ' '.join(filtered_words) if filtered_words else None
    
    def _open_application(self, app_info):
        """Try to open an application"""
        try:
            if self.system == "Windows":
                return self._open_windows_app(app_info)
            elif self.system == "Darwin":  # macOS
                return self._open_mac_app(app_info)
            else:  # Linux
                return self._open_linux_app(app_info)
        except Exception as e:
            print(f"Error opening application: {e}")
            return False
    
    def _open_windows_app(self, app_info):
        """Open application on Windows"""
        executable = app_info['executable']
        
        # Try common installation paths
        common_paths = [
            f"C:\\Program Files\\{executable}",
            f"C:\\Program Files (x86)\\{executable}",
            f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Local\\Programs\\{executable}",
            f"C:\\Windows\\System32\\{executable}",
            f"C:\\Windows\\{executable}"
        ]
        
        # Try to run from PATH first
        try:
            subprocess.Popen(executable)
            return True
        except:
            pass
        
        # Try common paths
        for path in common_paths:
            if os.path.exists(path):
                subprocess.Popen(path)
                return True
        
        # Search in registry for installed programs
        try:
            return self._find_and_run_from_registry(app_info)
        except:
            pass
        
        # Search entire system (last resort)
        return self._search_and_run_executable(executable)
    
    def _find_and_run_from_registry(self, app_info):
        """Find application from Windows registry"""
        import winreg
        
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        for registry_path in registry_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    try:
                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        if any(name in display_name.lower() for name in app_info['names']):
                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                            exe_path = os.path.join(install_location, app_info['executable'])
                            if os.path.exists(exe_path):
                                subprocess.Popen(exe_path)
                                return True
                    except:
                        continue
                    finally:
                        winreg.CloseKey(subkey)
            except:
                continue
        return False
    
    def _search_and_run_executable(self, executable):
        """Search for executable in common directories"""
        search_paths = [
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Local",
            f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Roaming"
        ]
        
        for search_path in search_paths:
            for root, dirs, files in os.walk(search_path):
                if executable in files:
                    full_path = os.path.join(root, executable)
                    try:
                        subprocess.Popen(full_path)
                        return True
                    except:
                        continue
        return False
    
    def _open_mac_app(self, app_info):
        """Open application on macOS"""
        try:
            subprocess.run(['open', '-a', app_info['executable']], check=True)
            return True
        except:
            return False
    
    def _open_linux_app(self, app_info):
        """Open application on Linux"""
        try:
            subprocess.Popen([app_info['executable']])
            return True
        except:
            return False
    
    def _handle_system_control(self, user_input):
        """Handle system control commands"""
        if 'shutdown' in user_input:
            return self.shutdown_system()
        elif 'restart' in user_input:
            return self.restart_system()
        elif 'sleep' in user_input:
            return self.sleep_system()
        elif 'lock' in user_input:
            return self.lock_system()
    
    def _handle_file_operations(self, user_input):
        """Handle file operation commands"""
        if 'create folder' in user_input or 'create directory' in user_input:
            folder_name = self._extract_folder_name(user_input)
            return self.create_folder(folder_name)
        elif 'list files' in user_input:
            return self.list_files()
        # Add more file operations as needed
        return "I can help with file operations. What specifically would you like to do?"
    
    def _handle_system_info(self, user_input):
        """Handle system information requests"""
        if 'battery' in user_input:
            return self.get_battery_status()
        elif 'memory' in user_input:
            return self.get_memory_usage()
        elif 'disk' in user_input:
            return self.get_disk_usage()
        elif 'system' in user_input:
            return self.get_system_info()
        elif 'process' in user_input:
            return self.get_running_processes()
        elif 'network' in user_input:
            return self.get_network_info()
    
    def _handle_volume_control(self, user_input):
        """Handle volume control commands"""
        if 'volume up' in user_input or 'increase volume' in user_input:
            return self.volume_up()
        elif 'volume down' in user_input or 'decrease volume' in user_input:
            return self.volume_down()
        elif 'mute' in user_input and 'unmute' not in user_input:
            return self.mute_volume()
        elif 'unmute' in user_input:
            return self.unmute_volume()
    
    def _handle_web_tasks(self, user_input):
        """Handle web-related tasks"""
        if 'google' in user_input and 'search' in user_input:
            query = self._extract_search_query(user_input)
            return self.google_search(query)
        elif 'website' in user_input or 'browse' in user_input:
            url = self._extract_url(user_input)
            return self.open_website(url)
    
    def _handle_time_date(self, user_input):
        """Handle time and date requests"""
        if 'time' in user_input:
            return self.get_current_time()
        elif 'date' in user_input:
            return self.get_current_date()
    
    def _handle_weather(self, user_input):
        """Handle weather requests"""
        return self.get_weather()
    
    def _handle_conversation(self, user_input):
        """Handle basic conversation"""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        thanks = ['thank you', 'thanks', 'appreciate']
        goodbyes = ['bye', 'goodbye', 'see you', 'exit', 'quit']
        
        if any(greeting in user_input for greeting in greetings):
            return "Hello! I'm your AI assistant. I can help you with computer tasks like opening applications, managing files, controlling system settings, and much more. What would you like me to do?"
        
        elif any(thank in user_input for thank in thanks):
            return "You're welcome! Is there anything else I can help you with?"
        
        elif any(goodbye in user_input for goodbye in goodbyes):
            return "Goodbye! Feel free to ask for help anytime."
        
        elif 'help' in user_input:
            return self._get_help_message()
        
        else:
            return "I'm here to help with computer tasks. You can ask me to open applications, check system info, manage files, control volume, and much more. What would you like me to do?"
    
    def _get_help_message(self):
        """Generate help message"""
        return """
Here's what I can help you with:

📱 **Applications**: Open any installed app (e.g., "open Chrome", "launch VS Code")

🖥️ **System Control**: 
- Shutdown, restart, sleep, or lock your computer
- Check battery, memory, disk usage
- View running processes

🔊 **Volume Control**: 
- Increase/decrease volume
- Mute/unmute audio

📁 **File Management**:
- List files, create folders
- Copy, move, or delete files
- Search for files

🌐 **Web Tasks**:
- Google search anything
- Open websites

⏰ **Information**:
- Current time and date
- Weather information
- System specifications

💬 **Conversation**: Just chat with me naturally!

Just tell me what you'd like to do in plain English!
        """
    
    # System Information Methods
    def get_system_info(self):
        """Get system information"""
        info = {
            'OS': f"{platform.system()} {platform.release()}",
            'Processor': platform.processor(),
            'Architecture': platform.architecture()[0],
            'Hostname': platform.node(),
            'Python Version': platform.python_version()
        }
        
        result = "🖥️ **System Information:**\n"
        for key, value in info.items():
            result += f"• {key}: {value}\n"
        
        return result
    
    def get_battery_status(self):
        """Get battery status"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                status = "Plugged in" if battery.power_plugged else "Not plugged in"
                return f"🔋 **Battery Status:**\n• Level: {battery.percent}%\n• Status: {status}"
            else:
                return "🔋 Battery information not available (desktop computer?)"
        except:
            return "❌ Unable to get battery information"
    
    def get_memory_usage(self):
        """Get memory usage"""
        try:
            memory = psutil.virtual_memory()
            return f"💾 **Memory Usage:**\n• Total: {self._bytes_to_gb(memory.total):.1f} GB\n• Used: {self._bytes_to_gb(memory.used):.1f} GB ({memory.percent}%)\n• Available: {self._bytes_to_gb(memory.available):.1f} GB"
        except:
            return "❌ Unable to get memory information"
    
    def get_disk_usage(self):
        """Get disk usage"""
        try:
            disk = psutil.disk_usage('/')
            return f"💽 **Disk Usage:**\n• Total: {self._bytes_to_gb(disk.total):.1f} GB\n• Used: {self._bytes_to_gb(disk.used):.1f} GB\n• Free: {self._bytes_to_gb(disk.free):.1f} GB"
        except:
            return "❌ Unable to get disk information"
    
    def get_running_processes(self):
        """Get running processes (top 10 by CPU usage)"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    processes.append(proc.info)
                except:
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            result = "🔄 **Top Processes (by CPU usage):**\n"
            for i, proc in enumerate(processes[:10]):
                result += f"• {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent'] or 0}%\n"
            
            return result
        except:
            return "❌ Unable to get process information"
    
    def get_network_info(self):
        """Get network information"""
        try:
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            result = "🌐 **Network Information:**\n"
            for interface, addresses in interfaces.items():
                if interface in stats and stats[interface].isup:
                    for addr in addresses:
                        if addr.family == 2:  # IPv4
                            result += f"• {interface}: {addr.address}\n"
            
            return result
        except:
            return "❌ Unable to get network information"
    
    # System Control Methods
    def shutdown_system(self):
        """Shutdown the system"""
        try:
            if self.system == "Windows":
                os.system("shutdown /s /t 5")
            elif self.system == "Darwin":
                os.system("sudo shutdown -h +1")
            else:
                os.system("shutdown -h +1")
            return "🔴 System will shutdown in 5 seconds..."
        except:
            return "❌ Unable to shutdown system"
    
    def restart_system(self):
        """Restart the system"""
        try:
            if self.system == "Windows":
                os.system("shutdown /r /t 5")
            elif self.system == "Darwin":
                os.system("sudo shutdown -r +1")
            else:
                os.system("shutdown -r +1")
            return "🔄 System will restart in 5 seconds..."
        except:
            return "❌ Unable to restart system"
    
    def sleep_system(self):
        """Put system to sleep"""
        try:
            if self.system == "Windows":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            elif self.system == "Darwin":
                os.system("pmset sleepnow")
            else:
                os.system("systemctl suspend")
            return "😴 Putting system to sleep..."
        except:
            return "❌ Unable to put system to sleep"
    
    def lock_system(self):
        """Lock the system"""
        try:
            if self.system == "Windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            elif self.system == "Darwin":
                os.system("/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend")
            else:
                os.system("gnome-screensaver-command -l")
            return "🔒 System locked"
        except:
            return "❌ Unable to lock system"
    
    # Volume Control Methods
    def volume_up(self):
        """Increase volume"""
        try:
            if self.system == "Windows":
                import winsound
                # This is a simplified approach
                os.system("nircmd.exe changesysvolume 2000")
            return "🔊 Volume increased"
        except:
            return "❌ Unable to control volume"
    
    def volume_down(self):
        """Decrease volume"""
        try:
            if self.system == "Windows":
                os.system("nircmd.exe changesysvolume -2000")
            return "🔉 Volume decreased"
        except:
            return "❌ Unable to control volume"
    
    def mute_volume(self):
        """Mute volume"""
        try:
            if self.system == "Windows":
                os.system("nircmd.exe mutesysvolume 1")
            return "🔇 Volume muted"
        except:
            return "❌ Unable to mute volume"
    
    def unmute_volume(self):
        """Unmute volume"""
        try:
            if self.system == "Windows":
                os.system("nircmd.exe mutesysvolume 0")
            return "🔊 Volume unmuted"
        except:
            return "❌ Unable to unmute volume"
    
    #