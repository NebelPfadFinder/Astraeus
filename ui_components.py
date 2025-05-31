# v2
"""
Modern Chatbot UI Components
Consolidated UI components for Mistral API chatbot with Qdrant integration
"""

import streamlit as st
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
import json

class ModernChatUI:
    """Modern chatbot UI with integrated styling and components"""
    
    def __init__(self):
        self.colors = {
            'primary': '#1e3a5f',      # Navy blue
            'secondary': '#4a7c7e',    # Teal
            'accent': '#7a9471',       # Sage green
            'success': '#8faa6f',      # Olive green
            'background': '#f5f2e8',   # Cream
            'text_primary': '#2c3e50',
            'text_secondary': '#5a6c7d',
            'border': '#e0ddd4',
            'shadow': 'rgba(30, 58, 95, 0.1)'
        }
        self.apply_modern_css()
    
    def apply_modern_css(self):
        """Apply modern CSS styling with the specified color palette"""
        css = f"""
        <style>
        /* Global Styles */
        .stApp {{
            background: linear-gradient(135deg, {self.colors['background']} 0%, #f8f6f0 100%);
        }}
        
        /* Custom Chat Container */
        .chat-container {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 32px {self.colors['shadow']};
            padding: 24px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
            border: 1px solid {self.colors['border']};
        }}
        
        /* Message Bubbles */
        .message-bubble {{
            padding: 16px 20px;
            border-radius: 20px;
            margin: 12px 0;
            max-width: 80%;
            word-wrap: break-word;
            position: relative;
            animation: slideIn 0.3s ease-out;
        }}
        
        .user-message {{
            background: linear-gradient(135deg, {self.colors['primary']} 0%, {self.colors['secondary']} 100%);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 16px rgba(30, 58, 95, 0.2);
        }}
        
        .bot-message {{
            background: linear-gradient(135deg, {self.colors['accent']} 0%, {self.colors['success']} 100%);
            color: white;
            margin-right: auto;
            border-bottom-left-radius: 4px;
            box-shadow: 0 4px 16px rgba(122, 148, 113, 0.2);
        }}
        
        .system-message {{
            background: {self.colors['background']};
            color: {self.colors['text_secondary']};
            text-align: center;
            font-style: italic;
            border: 1px dashed {self.colors['border']};
            margin: 8px auto;
        }}
        
        /* Typing Indicator */
        .typing-indicator {{
            display: flex;
            align-items: center;
            padding: 12px 20px;
            background: {self.colors['background']};
            border-radius: 20px;
            margin: 8px 0;
            border: 2px solid {self.colors['accent']};
            animation: pulse 2s infinite;
        }}
        
        .typing-dots {{
            display: flex;
            gap: 4px;
        }}
        
        .typing-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: {self.colors['accent']};
            animation: bounce 1.4s infinite;
        }}
        
        .typing-dot:nth-child(1) {{ animation-delay: -0.32s; }}
        .typing-dot:nth-child(2) {{ animation-delay: -0.16s; }}
        
        /* Input Styling */
        .stTextInput > div > div > input {{
            background: white;
            border: 2px solid {self.colors['border']};
            border-radius: 12px;
            padding: 12px 16px;
            font-size: 16px;
            transition: all 0.3s ease;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {self.colors['primary']};
            box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.1);
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {self.colors['primary']} 0%, {self.colors['secondary']} 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(30, 58, 95, 0.2);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(30, 58, 95, 0.3);
        }}
        
        /* Quick Actions */
        .quick-actions {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin: 16px 0;
        }}
        
        .quick-action-btn {{
            background: {self.colors['background']};
            color: {self.colors['text_primary']};
            border: 2px solid {self.colors['accent']};
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .quick-action-btn:hover {{
            background: {self.colors['accent']};
            color: white;
            transform: scale(1.05);
        }}
        
        /* Sidebar Styling */
        .sidebar-section {{
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin: 12px 0;
            border: 1px solid {self.colors['border']};
            box-shadow: 0 2px 8px {self.colors['shadow']};
        }}
        
        /* Progress Bar */
        .modern-progress {{
            width: 100%;
            height: 8px;
            background: {self.colors['border']};
            border-radius: 4px;
            overflow: hidden;
            margin: 8px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, {self.colors['primary']}, {self.colors['secondary']});
            border-radius: 4px;
            transition: width 0.3s ease;
        }}
        
        /* Notifications */
        .notification {{
            padding: 12px 16px;
            border-radius: 8px;
            margin: 8px 0;
            animation: slideDown 0.3s ease-out;
        }}
        
        .notification.success {{
            background: rgba(143, 170, 111, 0.1);
            border-left: 4px solid {self.colors['success']};
            color: #2d5016;
        }}
        
        .notification.error {{
            background: rgba(231, 76, 60, 0.1);
            border-left: 4px solid #e74c3c;
            color: #c0392b;
        }}
        
        .notification.info {{
            background: rgba(74, 124, 126, 0.1);
            border-left: 4px solid {self.colors['secondary']};
            color: #2c5f61;
        }}
        
        /* Animations */
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes slideDown {{
            from {{
                opacity: 0;
                transform: translateY(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes bounce {{
            0%, 80%, 100% {{
                transform: scale(0);
            }}
            40% {{
                transform: scale(1);
            }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: 0.5;
            }}
        }}
        
        /* Status Indicators */
        .status-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .status-online {{
            background: rgba(143, 170, 111, 0.2);
            color: {self.colors['success']};
        }}
        
        .status-offline {{
            background: rgba(231, 76, 60, 0.2);
            color: #e74c3c;
        }}
        
        .status-processing {{
            background: rgba(74, 124, 126, 0.2);
            color: {self.colors['secondary']};
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .message-bubble {{
                max-width: 95%;
            }}
            
            .chat-container {{
                margin: 10px;
                padding: 16px;
            }}
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
        
        # Add JavaScript for enhanced interactions
        js = """
        <script>
        // Auto-scroll to bottom of chat
        function scrollToBottom() {
            window.scrollTo(0, document.body.scrollHeight);
        }
        
        // Enhanced message animations
        function animateMessage(element) {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            setTimeout(() => {
                element.style.transition = 'all 0.3s ease-out';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 100);
        }
        
        // Quick action handlers
        function handleQuickAction(action) {
            const inputField = document.querySelector('input[type="text"]');
            if (inputField) {
                inputField.value = action;
                inputField.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
        </script>
        """
        st.markdown(js, unsafe_allow_html=True)
    
    def create_message_bubble(self, message: str, sender: str, timestamp: Optional[datetime] = None) -> str:
        """Create a styled message bubble"""
        if timestamp is None:
            timestamp = datetime.now()
        
        time_str = timestamp.strftime("%H:%M")
        
        if sender == "user":
            bubble_class = "user-message"
            icon = "👤"
        elif sender == "bot":
            bubble_class = "bot-message"
            icon = "🤖"
        else:
            bubble_class = "system-message"
            icon = "ℹ️"
        
        return f"""
        <div class="message-bubble {bubble_class}">
            <div style="display: flex; align-items: flex-start; gap: 8px;">
                <span style="font-size: 16px;">{icon}</span>
                <div style="flex: 1;">
                    <div>{message}</div>
                    <div style="font-size: 11px; opacity: 0.7; margin-top: 4px;">{time_str}</div>
                </div>
            </div>
        </div>
        """
    
    def create_typing_indicator(self) -> str:
        """Create animated typing indicator"""
        return """
        <div class="typing-indicator">
            <span style="margin-right: 8px;">🤖</span>
            <span>AI is typing</span>
            <div class="typing-dots" style="margin-left: 8px;">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
        """
    
    def create_progress_bar(self, progress: float, label: str = "") -> str:
        """Create a modern progress bar"""
        return f"""
        <div style="margin: 16px 0;">
            {f'<div style="font-size: 14px; color: {self.colors["text_secondary"]}; margin-bottom: 8px;">{label}</div>' if label else ''}
            <div class="modern-progress">
                <div class="progress-fill" style="width: {progress}%;"></div>
            </div>
            <div style="font-size: 12px; color: {self.colors['text_secondary']}; text-align: right; margin-top: 4px;">
                {progress:.1f}%
            </div>
        </div>
        """
    
    def show_notification(self, message: str, type: str = "info", duration: int = 3) -> None:
        """Display a notification"""
        notification_html = f"""
        <div class="notification {type}" id="notification-{int(time.time())}">
            {message}
        </div>
        <script>
        setTimeout(() => {{
            const notification = document.getElementById('notification-{int(time.time())}');
            if (notification) {{
                notification.style.transition = 'all 0.3s ease-out';
                notification.style.opacity = '0';
                notification.style.transform = 'translateY(-10px)';
                setTimeout(() => notification.remove(), 300);
            }}
        }}, {duration * 1000});
        </script>
        """
        st.markdown(notification_html, unsafe_allow_html=True)
    
    def display_system_status(self, mistral_status: bool, qdrant_status: bool) -> None:
        """Display system status indicators"""
        mistral_class = "status-online" if mistral_status else "status-offline"
        qdrant_class = "status-online" if qdrant_status else "status-offline"
        
        mistral_text = "Connected" if mistral_status else "Disconnected"
        qdrant_text = "Connected" if qdrant_status else "Disconnected"
        
        status_html = f"""
        <div style="display: flex; gap: 16px; margin: 16px 0; flex-wrap: wrap;">
            <div class="status-indicator {mistral_class}">
                <span>🧠</span>
                <span>Mistral AI: {mistral_text}</span>
            </div>
            <div class="status-indicator {qdrant_class}">
                <span>🔍</span>
                <span>Qdrant DB: {qdrant_text}</span>
            </div>
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)
    
    def render_quick_actions(self, actions: List[str]) -> str:
        """Render quick action buttons"""
        actions_html = '<div class="quick-actions">'
        for action in actions:
            actions_html += f'''
                <button class="quick-action-btn" onclick="handleQuickAction('{action}')">
                    {action}
                </button>
            '''
        actions_html += '</div>'
        return actions_html
    
    def render_chat_input(self, placeholder: str = "Type your message...") -> None:
        """Render the chat input with modern styling"""
        st.markdown(f"""
        <div style="position: sticky; bottom: 0; background: {self.colors['background']}; 
                    padding: 16px; border-top: 1px solid {self.colors['border']}; 
                    backdrop-filter: blur(10px);">
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar_section(self, title: str, content: str) -> None:
        """Render a styled sidebar section"""
        st.sidebar.markdown(f"""
        <div class="sidebar-section">
            <h3 style="color: {self.colors['primary']}; margin: 0 0 12px 0; font-size: 18px;">
                {title}
            </h3>
            <div style="color: {self.colors['text_secondary']};">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)


class ChatMessage:
    """Enhanced chat message class"""
    
    def __init__(self, content: str, sender: str, timestamp: Optional[datetime] = None, 
                 metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.sender = sender
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'content': self.content,
            'sender': self.sender,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create message from dictionary"""
        return cls(
            content=data['content'],
            sender=data['sender'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {})
        )


class ChatHistory:
    """Enhanced chat history management"""
    
    def __init__(self, max_messages: int = 100):
        self.messages: List[ChatMessage] = []
        self.max_messages = max_messages
    
    def add_message(self, message: ChatMessage) -> None:
        """Add a message to history"""
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def get_recent_messages(self, count: int = 10) -> List[ChatMessage]:
        """Get recent messages"""
        return self.messages[-count:] if count < len(self.messages) else self.messages
    
    def clear_history(self) -> None:
        """Clear all messages"""
        self.messages.clear()
    
    def export_history(self) -> str:
        """Export history as JSON"""
        return json.dumps([msg.to_dict() for msg in self.messages], indent=2)
    
    def import_history(self, json_str: str) -> None:
        """Import history from JSON"""
        data = json.loads(json_str)
        self.messages = [ChatMessage.from_dict(msg) for msg in data]


# Usage example and helper functions
def initialize_chat_ui() -> ModernChatUI:
    """Initialize the modern chat UI"""
    if 'chat_ui' not in st.session_state:
        st.session_state.chat_ui = ModernChatUI()
    return st.session_state.chat_ui

def initialize_chat_history() -> ChatHistory:
    """Initialize chat history"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = ChatHistory()
    return st.session_state.chat_history
