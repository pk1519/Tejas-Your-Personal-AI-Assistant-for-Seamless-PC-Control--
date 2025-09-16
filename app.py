import streamlit as st
import os
import json
import pyttsx3
import threading
from datetime import datetime, timedelta
from ai_core import handle_task, llm_fallback, recognize_voice
import time
import psutil

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
if 'enable_speech_output' not in st.session_state:
    st.session_state.enable_speech_output = False

# Custom CSS for better styling
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
    
    .sidebar .element-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

def speak_text(text):
    """Convert text to speech using pyttsx3"""
    if st.session_state.enable_speech_output and text:
        try:
            def speak():
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
            
            # Run TTS in a separate thread to avoid blocking
            threading.Thread(target=speak, daemon=True).start()
        except Exception as e:
            st.error(f"Speech error: {e}")

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
        disk = psutil.disk_usage('/')
        
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
        st.error(f"Error getting system metrics: {e}")
        return None

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
        
        # Voice settings
        st.subheader("🔊 Voice Settings")
        st.session_state.enable_speech_output = st.checkbox(
            "Enable Voice Output",
            value=st.session_state.enable_speech_output
        )
        
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
                ai_response = handle_task("show system information", llm_fallback_func=llm_fallback)
                add_message_to_chat('user', 'Show system information')
                add_message_to_chat('ai', ai_response)
                speak_text(ai_response)
                st.rerun()
        
        with col2:
            if st.button("🌐 Network Info"):
                ai_response = handle_task("show network information", llm_fallback_func=llm_fallback)
                add_message_to_chat('user', 'Show network information')
                add_message_to_chat('ai', ai_response)
                speak_text(ai_response)
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
            placeholder="Ask me to open apps, check system info, manage files, and more!",
            key="user_input"
        )
        
        col_send, col_voice = st.columns([3, 1])
        
        with col_send:
            if st.button("📤 Send", type="primary") and user_input:
                # Add user message to chat
                add_message_to_chat('user', user_input)
                
                # Get AI response
                try:
                    ai_response = handle_task(user_input, llm_fallback_func=llm_fallback)
                    add_message_to_chat('ai', ai_response)
                    
                    # Speak if enabled
                    speak_text(ai_response)
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    add_message_to_chat('ai', error_msg)
                
                # Clear input and rerun
                st.session_state.user_input = ""
                st.rerun()
        
        with col_voice:
            if st.button("🎤 Voice Input"):
                st.info("🎤 Listening... Speak now!")
                
                # Placeholder for voice input (requires additional setup)
                try:
                    # Note: Voice recognition might not work well in Streamlit environment
                    # This is a placeholder for future implementation
                    voice_text = recognize_voice(duration=5)
                    if voice_text:
                        add_message_to_chat('user', f"🗣️ {voice_text}")
                        ai_response = handle_task(voice_text, llm_fallback_func=llm_fallback)
                        add_message_to_chat('ai', ai_response)
                        speak_text(ai_response)
                        st.rerun()
                    else:
                        st.warning("⚠️ No speech detected. Please try again.")
                except Exception as e:
                    st.error(f"❌ Voice recognition error: {str(e)}")
    
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
                ai_response = handle_task("list files in current directory", llm_fallback_func=llm_fallback)
                add_message_to_chat('user', 'List files in current directory')
                add_message_to_chat('ai', ai_response)
                st.rerun()
            
            folder_name = st.text_input("Create folder:", key="folder_input")
            if st.button("📁 Create Folder") and folder_name:
                ai_response = handle_task(f"create folder {folder_name}", llm_fallback_func=llm_fallback)
                add_message_to_chat('user', f'Create folder {folder_name}')
                add_message_to_chat('ai', ai_response)
                st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: rgba(255, 255, 255, 0.7); padding: 1rem;'>
        <p>🤖 <strong>Tejas AI</strong> - Streamlit Version | Empowering productivity through intelligent automation</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()