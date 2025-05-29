import streamlit as st
import re
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app."""
    custom_css = """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        margin: 1rem;
    }
    
    /* Title styling */
    h1 {
        color: #2c3e50;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #667eea;
    }
    
    .stChatMessage[data-testid="chat-message-user"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left: 4px solid #ffffff;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    }
    
    .sidebar .sidebar-content {
        background: transparent;
    }
    
    .sidebar h1, .sidebar h2, .sidebar h3 {
        color: white;
    }
    
    .sidebar .stMarkdown {
        color: #ecf0f1;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e1e8ed;
        padding: 0.75rem;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Chat input styling */
    .stChatInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e1e8ed;
        padding: 0.75rem 1.5rem;
        font-size: 16px;
        background: rgba(255, 255, 255, 0.9);
        transition: all 0.3s ease;
    }
    
    .stChatInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        background: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        border: 1px solid #e1e8ed;
        font-weight: 500;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 0 0 10px 10px;
        border: 1px solid #e1e8ed;
        border-top: none;
    }
    
    /* Metric styling */
    .metric-container {
        background: rgba(255, 255, 255, 0.8);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #667eea;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        border-radius: 10px;
        border: none;
    }
    
    .stError {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
        border-radius: 10px;
        border: none;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #ffa500 0%, #ff6b6b 100%);
        border-radius: 10px;
        border: none;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Animation for messages */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .stChatMessage {
        animation: slideIn 0.3s ease-out;
    }
    
    /* Dark mode adjustments */
    @media (prefers-color-scheme: dark) {
        .main .block-container {
            background: rgba(30, 30, 30, 0.95);
            color: #ecf0f1;
        }
        
        .stChatMessage[data-testid="chat-message-assistant"] {
            background: rgba(102, 126, 234, 0.2);
            color: #ecf0f1;
        }
    }
    
    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .main .block-container {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        h1 {
            font-size: 1.5rem;
        }
        
        .stChatMessage {
            padding: 0.75rem;
        }
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def format_message(content: str) -> str:
    """
    Format message content with enhanced markdown rendering.
    
    Args:
        content: Raw message content
        
    Returns:
        Formatted message content
    """
    if not content:
        return ""
    
    try:
        # Enhanced code block detection and formatting
        content = re.sub(
            r'```(\w+)?\n(.*?)\n```',
            r'```\1\n\2\n```',
            content,
            flags=re.DOTALL
        )
        
        # Enhance bold and italic formatting
        content = re.sub(r'\*\*(.*?)\*\*', r'**\1**', content)
        content = re.sub(r'\*(.*?)\*', r'*\1*', content)
        
        # Add line breaks for better readability
        content = re.sub(r'\n\n+', '\n\n', content)
        
        return content.strip()
        
    except Exception as e:
        logger.error(f"Error formatting message: {str(e)}")
        return content

def create_animated_typing_indicator():
    """Create an animated typing indicator."""
    typing_html = """
    <div style="display: flex; align-items: center; padding: 10px;">
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        <span style="margin-left: 10px; color: #666; font-style: italic;">AI is thinking...</span>
    </div>
    
    <style>
    .typing-indicator {
        display: flex;
        gap: 4px;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #667eea;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: 0s; }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }
    </style>
    """
    return typing_html

def create_message_bubble(content: str, is_user: bool = False, timestamp: str = None) -> str:
    """
    Create a styled message bubble.
    
    Args:
        content: Message content
        is_user: Whether the message is from user
        timestamp: Optional timestamp
        
    Returns:
        HTML string for the message bubble
    """
    bubble_class = "user-bubble" if is_user else "assistant-bubble"
    time_str = f'<div class="message-time">{timestamp}</div>' if timestamp else ""
    
    bubble_html = f"""
    <div class="message-container {bubble_class}">
        <div class="message-content">
            {content}
        </div>
        {time_str}
    </div>
    
    <style>
    .message-container {{
        margin: 10px 0;
        padding: 12px 16px;
        border-radius: 18px;
        max-width: 80%;
        word-wrap: break-word;
        animation: slideIn 0.3s ease-out;
    }}
    
    .user-bubble {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        text-align: right;
    }}
    
    .assistant-bubble {{
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.2);
        margin-right: auto;
    }}
    
    .message-time {{
        font-size: 0.8em;
        opacity: 0.7;
        margin-top: 5px;
    }}
    </style>
    """
    return bubble_html

def display_system_status(mistral_status: bool, qdrant_status: bool):
    """
    Display system status indicators.
    
    Args:
        mistral_status: Mistral API status
        qdrant_status: Qdrant database status
    """
    col1, col2 = st.columns(2)
    
    with col1:
        status_color = "🟢" if mistral_status else "🔴"
        st.write(f"{status_color} Mistral AI: {'Connected' if mistral_status else 'Disconnected'}")
    
    with col2:
        status_color = "🟢" if qdrant_status else "🔴"
        st.write(f"{status_color} Qdrant DB: {'Connected' if qdrant_status else 'Disconnected'}")

def create_progress_bar(progress: float, text: str = ""):
    """
    Create a custom progress bar.
    
    Args:
        progress: Progress value (0.0 to 1.0)
        text: Optional progress text
    """
    progress_html = f"""
    <div class="custom-progress">
        <div class="progress-bar" style="width: {progress * 100}%"></div>
        <div class="progress-text">{text}</div>
    </div>
    
    <style>
    .custom-progress {{
        background: #e1e8ed;
        border-radius: 10px;
        height: 20px;
        position: relative;
        overflow: hidden;
        margin: 10px 0;
    }}
    
    .progress-bar {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }}
    
    .progress-text {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 0.8em;
        font-weight: 500;
        color: #2c3e50;
    }}
    </style>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

def show_notification(message: str, notification_type: str = "info"):
    """
    Show a styled notification.
    
    Args:
        message: Notification message
        notification_type: Type of notification (info, success, warning, error)
    """
    color_map = {
        "info": "#3498db",
        "success": "#2ecc71", 
        "warning": "#f39c12",
        "error": "#e74c3c"
    }
    
    color = color_map.get(notification_type, "#3498db")
    
    notification_html = f"""
    <div class="notification {notification_type}">
        <div class="notification-content">
            {message}
        </div>
    </div>
    
    <style>
    .notification {{
        padding: 12px 16px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid {color};
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.3s ease-out;
    }}
    
    .notification-content {{
        color: #2c3e50;
        font-weight: 500;
    }}
    </style>
    """
    st.markdown(notification_html, unsafe_allow_html=True)
