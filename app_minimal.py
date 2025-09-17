import streamlit as st
import os
import psutil
import platform
import subprocess
import webbrowser
from datetime import datetime
import time

# Configure Streamlit page
st.set_page_config(
    page_title="🤖 Tejas AI - Intelligent Desktop Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'reminders' not in st.session_state:
    st.session_state.reminders = []

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-header {
        text-align: center;
        color: white;
        padding: 1rem;
        margin-bottom: 2rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .user-message {
        background: rgba(100, 181, 246, 0.2);
        border-left: 4px solid #64B5F6;
    }
    
    .ai-message {
        background: rgba(76, 175, 80, 0.2);
        border-left: 4px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

def add_message_to_chat(role, content):
    """Add a message to chat history"""
    st.session_state.chat_history.append({
        'role': role,
        'content': content,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })

def display_chat_history():
    """Display chat history"""
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You ({message['timestamp']}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>🤖 AI Assistant ({message['timestamp']}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)

def get_system_metrics():
    """Get current system metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        try:
            if platform.system() == 'Windows':
                disk = psutil.disk_usage('C:\\')
            else:
                disk = psutil.disk_usage('/')
        except:
            disk = psutil.disk_usage('.')
        
        return {
            'cpu': cpu_percent,
            'memory': memory.percent,
            'disk': disk.percent,
            'memory_used': memory.used / (1024**3),
            'memory_total': memory.total / (1024**3),
            'disk_used': disk.used / (1024**3),
            'disk_total': disk.total / (1024**3)
        }
    except Exception as e:
        st.warning(f"Some system metrics may not be available: {e}")
        return {
            'cpu': 0, 'memory': 0, 'disk': 0,
            'memory_used': 0, 'memory_total': 0,
            'disk_used': 0, 'disk_total': 0
        }

def process_command(user_input):
    """Process user commands"""
    user_input = user_input.lower().strip()
    
    # System information
    if any(keyword in user_input for keyword in ['system', 'info', 'information']):
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
    
    # Memory usage
    elif any(keyword in user_input for keyword in ['memory', 'ram']):
        try:
            memory = psutil.virtual_memory()
            return f"💾 **Memory Usage:**\n• Total: {memory.total / (1024**3):.1f} GB\n• Used: {memory.used / (1024**3):.1f} GB ({memory.percent}%)\n• Available: {memory.available / (1024**3):.1f} GB"
        except:
            return "❌ Unable to get memory information"
    
    # Time/Date
    elif 'time' in user_input:
        current_time = datetime.now().strftime("%I:%M:%S %p")
        return f"🕐 Current time: {current_time}"
    
    elif 'date' in user_input:
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        return f"📅 Current date: {current_date}"
    
    # Web search
    elif 'search' in user_input:
        words = user_input.split()
        query_words = [word for word in words if word not in ['google', 'search', 'for', 'please', 'can', 'you']]
        query = ' '.join(query_words) if query_words else "search query"
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"🔍 Searching Google for: {query}"
    
    # File operations
    elif 'list files' in user_input:
        try:
            path = os.getcwd()
            files = os.listdir(path)
            result = f"📁 **Files in {path}:**\n"
            
            folders = [f for f in files if os.path.isdir(os.path.join(path, f))]
            files_only = [f for f in files if os.path.isfile(os.path.join(path, f))]
            
            for folder in sorted(folders):
                result += f"📂 {folder}/\n"
            
            for file in sorted(files_only):
                result += f"📄 {file}\n"
            
            return result
        except Exception as e:
            return f"❌ Unable to list files: {str(e)}"
    
    # Create folder
    elif 'create folder' in user_input:
        words = user_input.split()
        try:
            if 'folder' in words:
                idx = words.index('folder')
                if idx + 1 < len(words):
                    folder_name = ' '.join(words[idx + 1:])
                    os.makedirs(folder_name, exist_ok=True)
                    return f"✅ Folder '{folder_name}' created successfully"
            return "❌ Please specify a folder name"
        except Exception as e:
            return f"❌ Unable to create folder: {str(e)}"
    
    # Greetings and conversation
    elif any(greeting in user_input for greeting in ['hello', 'hi', 'hey']):
        return "Hello! I'm your AI assistant. I can help you with system information, file management, web searches, and more. What would you like me to do?"
    
    elif any(thank in user_input for thank in ['thank', 'thanks']):
        return "You're welcome! Is there anything else I can help you with?"
    
    elif 'help' in user_input:
        return """
Here's what I can help you with:

🖥️ **System Information**: 
- "Show system information"
- "Check memory usage"

📁 **File Management**:
- "List files"
- "Create folder [name]"

🌐 **Web Tasks**:
- "Search for [query]"

⏰ **Information**:
- "What time is it?"
- "What's the date?"

💬 **Conversation**: Just chat with me naturally!
        """
    
    # Cloud environment message
    elif any(keyword in user_input for keyword in ['model', 'voice', 'speech']):
        return """🌍 **Cloud Environment Detected**

Speech recognition features are not available in Streamlit Cloud.
For full functionality including voice recognition, please run locally:

```bash
pip install -r requirements-local.txt
streamlit run app.py
```

💡 **Cloud Features Available:**
• Full chat interface
• System monitoring  
• File management
• Web searches
• Application launching"""
    
    else:
        return "I'm here to help with computer tasks. You can ask me about system info, file management, web searches, and more. Type 'help' for a full list of commands!"

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Tejas AI - Intelligent Desktop Assistant</h1>
        <p>Your personal AI assistant for computer tasks, system monitoring, and productivity</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("🧭 Control Panel")
        
        # System metrics
        st.subheader("⚡ System Metrics")
        metrics = get_system_metrics()
        if metrics:
            st.metric("CPU Usage", f"{metrics['cpu']:.1f}%")
            st.metric("Memory Usage", f"{metrics['memory']:.1f}%", 
                     f"{metrics['memory_used']:.1f}GB / {metrics['memory_total']:.1f}GB")
            st.metric("Disk Usage", f"{metrics['disk']:.1f}%",
                     f"{metrics['disk_used']:.1f}GB / {metrics['disk_total']:.1f}GB")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 System Info"):
                response = process_command("show system information")
                add_message_to_chat('user', 'Show system information')
                add_message_to_chat('ai', response)
                st.rerun()
        
        with col2:
            if st.button("💾 Memory Info"):
                response = process_command("show memory usage")
                add_message_to_chat('user', 'Show memory usage')
                add_message_to_chat('ai', response)
                st.rerun()

        # Clear chat
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat interface
        st.subheader("💬 Chat with AI Assistant")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            display_chat_history()
        
        # Input area
        st.markdown("---")
        user_input = st.text_input(
            "💬 Type your message here...", 
            placeholder="Ask me to check system info, list files, search the web, and more!",
            key="user_input"
        )
        
        if st.button("📤 Send", type="primary") and user_input:
            # Add user message to chat
            add_message_to_chat('user', user_input)
            
            # Get AI response
            try:
                ai_response = process_command(user_input)
                add_message_to_chat('ai', ai_response)
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                add_message_to_chat('ai', error_msg)
            
            # Clear input and rerun
            st.session_state.user_input = ""
            st.rerun()
    
    with col2:
        # Tools panel
        st.subheader("🛠️ Tools")
        
        # Reminder tool
        with st.expander("📅 Quick Reminder"):
            reminder_text = st.text_input("Reminder:", key="reminder_input")
            if st.button("Add Reminder") and reminder_text:
                reminder = {
                    'text': reminder_text,
                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'completed': False
                }
                st.session_state.reminders.append(reminder)
                st.success("✅ Reminder added!")
        
        # Display reminders
        if st.session_state.reminders:
            st.subheader("📋 Active Reminders")
            for i, reminder in enumerate(st.session_state.reminders):
                if not reminder['completed']:
                    col_text, col_done = st.columns([3, 1])
                    with col_text:
                        st.write(f"• {reminder['text']}")
                        st.caption(f"Added: {reminder['time']}")
                    with col_done:
                        if st.button("✓", key=f"complete_{i}"):
                            st.session_state.reminders[i]['completed'] = True
                            st.rerun()
        
        # File operations
        with st.expander("📁 File Operations"):
            if st.button("📂 List Current Directory"):
                response = process_command("list files in current directory")
                add_message_to_chat('user', 'List files in current directory')
                add_message_to_chat('ai', response)
                st.rerun()
            
            folder_name = st.text_input("Create folder:", key="folder_input")
            if st.button("📁 Create Folder") and folder_name:
                response = process_command(f"create folder {folder_name}")
                add_message_to_chat('user', f'Create folder {folder_name}')
                add_message_to_chat('ai', response)
                st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: rgba(255, 255, 255, 0.7); padding: 1rem;'>
        <p>🤖 <strong>Tejas AI</strong> - Cloud Version | Empowering productivity through intelligent automation</p>
        <p>💡 For full features including voice recognition, run locally with requirements-local.txt</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()