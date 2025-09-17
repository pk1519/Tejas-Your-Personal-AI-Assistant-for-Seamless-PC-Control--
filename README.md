# Tejas AI – Intelligent Desktop Assistant (Streamlit Version)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Cross%20Platform-green.svg)](https://streamlit.io)

**Tejas AI** is a sophisticated, AI-powered desktop assistant built with Streamlit. This version provides an intuitive web-based interface for system automation, natural language processing, and productivity tools without requiring authentication or database dependencies.

## 🚀 Key Features

### 💬 **Interactive Web Interface**
- **Streamlit-powered UI**: Modern, responsive web interface accessible from any browser
- **Real-time Chat Interface**: Conversational AI interaction with persistent chat history
- **Advanced Voice Integration**: Multi-engine speech recognition with automatic model selection
- **Cross-platform Compatibility**: Runs on Windows, macOS, and Linux

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
- **Session-based Reminders**: Quick reminder system with completion tracking
- **File Management**: Create folders, list directories, and manage files
- **Quick Actions**: One-click access to common system tasks

### 🤖 **Intelligent Speech Recognition**
- **Automatic Model Selection**: Scans and selects the best available speech recognition model
- **Multi-Engine Support**: Vosk (offline), Google Speech API, Sphinx fallback
- **Model Management**: Real-time model information and performance metrics
- **Offline Capability**: Works without internet using local Vosk models
- **Performance Optimization**: Automatic model scoring and selection based on accuracy and size

### 👨‍🎨 **Modern User Experience**
- **Streamlit Interface**: Clean, modern web-based user interface
- **Responsive Design**: Works seamlessly on desktop and mobile browsers
- **Real-time Updates**: Live system metrics and interactive feedback

## 📋 Prerequisites

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.8 or higher
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: 200MB available space
- **Web Browser**: Modern browser (Chrome, Firefox, Safari, Edge)
- **Internet**: Required for Streamlit Cloud deployment and web features

## 🛠️ Installation

### 1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/TejasAi-Streamlit.git
cd TejasAi-Streamlit
```

### 2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Run the Application**
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 🚀 Quick Start

### **Launch the Application**
```bash
streamlit run app.py
```

### **Using the Interface**
1. **Open your browser** to `http://localhost:8501`
2. **Chat Interface**: Type messages in the chat input box
3. **Voice Output**: Toggle speech output in the sidebar
4. **System Metrics**: View real-time system performance
5. **Quick Tools**: Use reminders and file operations from the tools panel

### **Basic Usage Examples**
- **System Control**: "Show system information" or "Check memory usage"
- **File Management**: "List files" or "Create folder MyProject"
- **Web Search**: "Search for Python tutorials"
- **App Launch**: "Open Notepad" or "Launch Chrome"
- **Speech Models**: "Show model information" or "Refresh models"

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

# Speech Recognition
"Show model information"
"Refresh speech models"
"Which voice model are you using?"
```

### **Text Input**
- Type commands directly in the dashboard
- Use natural language for complex requests
- Access help and documentation

## 🏠 Architecture

### **Core Components**
- **`app.py`**: Main Streamlit application and user interface
- **`ai_core.py`**: AI processing and command interpretation engine
- **`model_manager.py`**: Intelligent speech model scanning and selection system
- **`requirements.txt`**: Python dependencies and packages
- **`.streamlit/config.toml`**: Streamlit configuration settings

### **Technology Stack**
- **Frontend**: Streamlit web framework with custom CSS styling
- **AI Engine**: Natural language processing and task automation
- **System Integration**: Cross-platform system monitoring via psutil
- **Speech Recognition**: Multi-engine support (Vosk, Google API, Sphinx)
- **Model Management**: Automatic scanning, scoring, and selection system
- **Voice Processing**: Text-to-speech using pyttsx3 with offline capability
- **State Management**: Streamlit session state for data persistence

## ⚙️ Configuration

### **Streamlit Configuration**
Create `.streamlit/config.toml` for custom settings:
```toml
[theme]
base = "dark"
primaryColor = "#64B5F6"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"

[server]
port = 8501
headless = false
```

### **Customization Options**
- Theme colors and styling
- Speech output preferences
- System monitoring intervals
- Chat interface behavior
- File operation permissions

## 🔧 Troubleshooting

### **Common Issues**

#### **Streamlit Not Starting**
- Ensure port 8501 is not in use by another application
- Check Python version compatibility (3.8+)
- Verify all dependencies are installed correctly

#### **Voice/Audio Issues**
- Text-to-speech may not work in browser environment
- Check system audio settings
- Ensure speakers/headphones are connected

#### **System Commands Not Working**
- Some system commands require elevated permissions
- File operations are limited to accessible directories
- Network commands may vary by operating system

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

- **Streamlit**: Modern web app framework for Python
- **psutil**: Cross-platform system monitoring library
- **pyttsx3**: Text-to-speech conversion library
- **SpeechRecognition**: Audio processing and recognition
- **Open Source Community**: Contributors and maintainers

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/TejasAi/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/TejasAi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/TejasAi/discussions)
- **Email**: support@tejasai.com

## 🔮 Roadmap

- [ ] **Streamlit Cloud Deployment**: One-click deployment to Streamlit Cloud
- [ ] **Enhanced Voice Integration**: Improved browser-based voice recognition
- [ ] **Plugin System**: Extensible architecture for custom commands
- [ ] **Multi-user Support**: Session management for multiple users
- [ ] **API Integration**: RESTful API endpoints for external services
- [ ] **Mobile Responsive**: Enhanced mobile browser experience

---

**Made with ❤️ by the Tejas AI Team**

*Empowering productivity through intelligent automation*


