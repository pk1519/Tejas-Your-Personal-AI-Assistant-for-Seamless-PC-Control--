# Tejas AI – Intelligent Desktop Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://microsoft.com/windows)

**Tejas AI** is a sophisticated, AI-powered desktop assistant designed for Windows systems. It combines cutting-edge offline voice recognition, natural language processing, and comprehensive system automation capabilities to provide an intuitive and powerful user experience.

## 🚀 Key Features

### 🎤 **Advanced Voice & Text Interface**
- **Offline Voice Recognition**: Powered by Vosk for real-time, privacy-focused speech processing
- **Dual Input Methods**: Voice commands and text input for maximum accessibility
- **Intelligent Fallback**: LLM-based understanding for complex or unrecognized commands
- **Natural Speech Output**: High-quality text-to-speech using pyttsx3

### ⚙️ **Comprehensive System Control**
- **Audio Management**: Precise volume control with incremental adjustments
- **Display Control**: Brightness adjustment and Night Light toggle
- **System Monitoring**: Real-time CPU and RAM statistics
- **Network Management**: WiFi network switching and Bluetooth control
- **Power Operations**: System shutdown, restart, and sleep management

### 🔧 **Smart Automation & Integration**
- **Application Launcher**: Intelligent app discovery with download redirects
- **Web Integration**: Direct web search and YouTube content playback
- **Task Automation**: Streamlined workflow optimization

### 📝 **Productivity Tools**
- **Persistent Storage**: MongoDB-powered notes and reminders system
- **Data Retrieval**: Quick access to saved information
- **Cross-session Persistence**: Maintains user data across sessions

### 🎨 **Modern User Experience**
- **Glass Morphism UI**: Sleek, semi-transparent PyQt5 dashboard
- **Responsive Design**: Adaptive interface positioning
- **Accessibility Features**: Configurable speech output and visual feedback

## 📋 Prerequisites

- **Operating System**: Windows 10/11 (64-bit)
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 500MB available space
- **Microphone**: Required for voice commands
- **Internet**: Required for initial setup and web features

## 🛠️ Installation

### 1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/TejasAi.git
cd TejasAi
```

### 2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Download Voice Model**
The application automatically downloads the Vosk voice recognition model on first run.

### 4. **Configure Authentication**
- Set up Google OAuth credentials in `config.py`
- Configure MongoDB connection settings

## 🚀 Quick Start

### **Launch the Application**
```bash
python main.py
```

### **Initial Setup**
1. **Authentication**: Complete Google OAuth setup on first launch
2. **Robot Interface**: Click the robot overlay to access the dashboard
3. **Voice Setup**: Ensure microphone permissions are granted

### **Basic Usage**
- **Voice Commands**: "Increase volume by 20%"
- **System Control**: "Show CPU stats" or "Enable Night Light"
- **Web Search**: "Search for Python tutorials"
- **App Launch**: "Open Notepad" or "Launch Chrome"

## 📖 Usage Examples

### **Voice Commands**
```bash
# System Controls
"Set volume to 75%"
"Increase brightness by 30%"
"Show system performance"
"Switch to WiFi network 'HomeNetwork'"

# Application Management
"Open Microsoft Word"
"Launch Spotify"
"Start Visual Studio Code"

# Web Operations
"Search for machine learning tutorials"
"Play Despacito on YouTube"
"Open GitHub in browser"

# Productivity
"Save note: Meeting with team at 3 PM"
"Show my saved notes"
"Set reminder for tomorrow 9 AM"
```

### **Text Input**
- Type commands directly in the dashboard
- Use natural language for complex requests
- Access help and documentation

## 🏗️ Architecture

### **Core Components**
- **`main.py`**: Application entry point and main event loop
- **`robot_overlay.py`**: Desktop robot interface
- **`dashboard.py`**: Main glass-morphism dashboard
- **`ai_core.py`**: AI processing and command interpretation
- **`auth_manager.py`**: Google OAuth authentication
- **`database.py`**: MongoDB data persistence

### **Technology Stack**
- **Frontend**: PyQt5 with custom glass-morphism styling
- **Voice Processing**: Vosk offline speech recognition
- **AI Engine**: LLM-based natural language understanding
- **Database**: MongoDB for persistent data storage
- **Authentication**: Google OAuth 2.0
- **System Integration**: Windows API via pywin32

## ⚙️ Configuration

### **Environment Variables**
```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=tejas_ai

# Google OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

### **Customization Options**
- Voice recognition sensitivity
- Speech output preferences
- Dashboard positioning
- Theme customization
- Command aliases

## 🔧 Troubleshooting

### **Common Issues**

#### **Voice Recognition Not Working**
- Check microphone permissions
- Verify Vosk model installation
- Test microphone in Windows settings

#### **Authentication Errors**
- Verify Google OAuth credentials
- Check internet connectivity
- Clear browser cache and cookies

#### **MongoDB Connection Issues**
- Ensure MongoDB service is running
- Verify connection string format
- Check firewall settings

### **Performance Optimization**
- Close unnecessary background applications
- Ensure adequate RAM availability
- Update audio drivers
- Optimize Windows performance settings

## 🤝 Contributing

We welcome contributions to Tejas AI! Please read our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit your changes**: `git commit -m 'Add AmazingFeature'`
4. **Push to the branch**: `git push origin feature/AmazingFeature`
5. **Open a Pull Request**

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black .
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Vosk**: Offline speech recognition engine
- **PyQt5**: Cross-platform GUI framework
- **MongoDB**: Document database
- **Google OAuth**: Authentication services
- **Open Source Community**: Contributors and maintainers

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/TejasAi/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/TejasAi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/TejasAi/discussions)
- **Email**: support@tejasai.com

## 🔮 Roadmap

- [ ] **Multi-language Support**: Internationalization and localization
- [ ] **Mobile Companion App**: Cross-platform synchronization
- [ ] **Advanced AI Models**: Integration with GPT-4 and Claude
- [ ] **Plugin System**: Extensible architecture for third-party integrations
- [ ] **Cloud Sync**: Cross-device data synchronization
- [ ] **API Integration**: RESTful API for external services

---

**Made with ❤️ by the Tejas AI Team**

*Empowering productivity through intelligent automation*


