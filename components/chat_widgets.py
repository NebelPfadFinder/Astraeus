"""
Custom Streamlit Components for Chat Interface

This module provides enhanced chat widgets and UI components
for a better user experience in the AI chatbot application.

Author: AI Chatbot System
Date: 2024
"""

import streamlit as st
import time
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import json
import re
from pathlib import Path

# Import custom styling
def load_custom_css():
    """Load custom CSS for enhanced chat styling."""
    css_path = Path(__file__).parent.parent / "static" / "css" / "chat_styles.css"
    if css_path.exists():
        with open(css_path, 'r') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback inline CSS
        st.markdown("""
        <style>
        .chat-message {
            padding: 1rem;
            border-radius: 0.8rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
            animation: fadeIn 0.3s ease-in;
        }
        
        .chat-message.user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: 20%;
            text-align: right;
        }
        
        .chat-message.assistant {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            margin-right: 20%;
        }
        
        .chat-message.system {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            text-align: center;
            margin: 0 10%;
        }
        
        .message-content {
            font-size: 1rem;
            line-height: 1.5;
        }
        
        .message-timestamp {
            font-size: 0.8rem;
            opacity: 0.8;
            margin-top: 0.5rem;
        }
        
        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        
        .typing-indicator {
            display: flex;
            align-items: center;
            padding: 1rem;
            background: #f0f2f6;
            border-radius: 0.8rem;
            margin-bottom: 1rem;
            margin-right: 20%;
        }
        
        .typing-dots {
            display: flex;
            gap: 4px;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #999;
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .chat-input-container {
            position: sticky;
            bottom: 0;
            background: white;
            padding: 1rem;
            border-top: 1px solid #e0e0e0;
            border-radius: 1rem 1rem 0 0;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        }
        
        .quick-actions {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }
        
        .quick-action-btn {
            background: #f0f2f6;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.9rem;
        }
        
        .quick-action-btn:hover {
            background: #e0e2e6;
            transform: translateY(-1px);
        }
        
        .message-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.5rem;
            opacity: 0;
            transition: opacity 0.2s;
        }
        
        .chat-message:hover .message-actions {
            opacity: 1;
        }
        
        .action-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            padding: 0.3rem 0.6rem;
            border-radius: 15px;
            cursor: pointer;
            font-size: 0.8rem;
            color: inherit;
        }
        
        .action-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        </style>
        """, unsafe_allow_html=True)


class ChatMessage:
    """Represents a single chat message with enhanced functionality."""
    
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None, 
                 message_id: Optional[str] = None, metadata: Optional[Dict] = None):
        self.role = role  # 'user', 'assistant', 'system'
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.message_id = message_id or str(uuid.uuid4())
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for storage."""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'message_id': self.message_id,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create message from dictionary."""
        return cls(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            message_id=data['message_id'],
            metadata=data.get('metadata', {})
        )


class ChatHistory:
    """Manages chat history with persistence and search capabilities."""
    
    def __init__(self, max_messages: int = 50):
        self.max_messages = max_messages
        self.messages: List[ChatMessage] = []
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state for chat history."""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'current_session_id' not in st.session_state:
            st.session_state.current_session_id = str(uuid.uuid4())
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> ChatMessage:
        """Add a new message to the chat history."""
        message = ChatMessage(role, content, metadata=metadata)
        self.messages.append(message)
        st.session_state.chat_history.append(message.to_dict())
        
        # Trim history if it exceeds max length
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
            st.session_state.chat_history = st.session_state.chat_history[-self.max_messages:]
        
        return message
    
    def get_messages(self) -> List[ChatMessage]:
        """Get all messages in current session."""
        return [ChatMessage.from_dict(msg) for msg in st.session_state.chat_history]
    
    def clear_history(self):
        """Clear all chat history."""
        self.messages.clear()
        st.session_state.chat_history.clear()
        st.session_state.current_session_id = str(uuid.uuid4())
    
    def search_messages(self, query: str) -> List[ChatMessage]:
        """Search messages by content."""
        query_lower = query.lower()
        return [
            msg for msg in self.get_messages()
            if query_lower in msg.content.lower()
        ]
    
    def export_history(self) -> str:
        """Export chat history as JSON."""
        return json.dumps([msg.to_dict() for msg in self.get_messages()], indent=2)


class TypingIndicator:
    """Shows typing indicator during response generation."""
    
    def __init__(self):
        self.placeholder = None
    
    def show(self, message: str = "AI is thinking..."):
        """Show typing indicator."""
        if self.placeholder is None:
            self.placeholder = st.empty()
        
        self.placeholder.markdown(f"""
        <div class="typing-indicator">
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            <span style="margin-left: 1rem;">{message}</span>
        </div>
        """, unsafe_allow_html=True)
    
    def hide(self):
        """Hide typing indicator."""
        if self.placeholder:
            self.placeholder.empty()


def render_message(message: ChatMessage, show_actions: bool = True) -> None:
    """
    Render a single chat message with enhanced styling.
    
    Args:
        message (ChatMessage): Message to render
        show_actions (bool): Whether to show message actions
    """
    # Determine avatar and styling based on role
    if message.role == 'user':
        avatar = "👤"
        css_class = "user"
    elif message.role == 'assistant':
        avatar = "🤖"
        css_class = "assistant"
    else:
        avatar = "ℹ️"
        css_class = "system"
    
    # Format timestamp
    time_str = message.timestamp.strftime("%H:%M")
    
    # Build message actions
    actions_html = ""
    if show_actions and message.role in ['user', 'assistant']:
        actions_html = f"""
        <div class="message-actions">
            <button class="action-btn" onclick="copyToClipboard('{message.message_id}')">📋 Copy</button>
            <button class="action-btn" onclick="shareMessage('{message.message_id}')">📤 Share</button>
        </div>
        """
    
    # Render message
    message_html = f"""
    <div class="chat-message {css_class}" id="{message.message_id}">
        <div style="display: flex; align-items: flex-start;">
            <div class="message-avatar" style="background: rgba(255,255,255,0.2);">
                {avatar}
            </div>
            <div style="flex: 1;">
                <div class="message-content">{message.content}</div>
                <div class="message-timestamp">{time_str}</div>
                {actions_html}
            </div>
        </div>
    </div>
    """
    
    st.markdown(message_html, unsafe_allow_html=True)


def render_quick_actions() -> Optional[str]:
    """
    Render quick action buttons for common queries.
    
    Returns:
        Optional[str]: Selected quick action text
    """
    quick_actions = [
        "What can you help me with?",
        "Summarize my documents",
        "Find relevant information about...",
        "Explain a concept",
        "Help me with coding",
        "Clear chat history"
    ]
    
    st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
    
    cols = st.columns(len(quick_actions))
    selected_action = None
    
    for i, action in enumerate(quick_actions):
        with cols[i]:
            if st.button(action, key=f"quick_action_{i}", help=f"Click to: {action}"):
                if action == "Clear chat history":
                    return "CLEAR_HISTORY"
                else:
                    selected_action = action
    
    st.markdown('</div>', unsafe_allow_html=True)
    return selected_action


def render_chat_input(placeholder: str = "Type your message here...") -> Optional[str]:
    """
    Render enhanced chat input with features.
    
    Args:
        placeholder (str): Placeholder text for input
        
    Returns:
        Optional[str]: User input text
    """
    # Chat input container
    with st.container():
        # Quick actions
        quick_action = render_quick_actions()
        if quick_action:
            return quick_action
        
        # Main input area
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder=placeholder,
                key="chat_input",
                label_visibility="collapsed"
            )
        
        with col2:
            send_clicked = st.button("Send", type="primary", use_container_width=True)
        
        # Additional options
        with st.expander("Advanced Options", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                temperature = st.slider("Response Creativity", 0.0, 1.0, 0.7, 0.1)
            with col2:
                max_tokens = st.number_input("Max Response Length", 100, 2000, 500, 50)
            
            # Store in session state for use by the main app
            st.session_state.temperature = temperature
            st.session_state.max_tokens = max_tokens
        
        # Return input if send clicked or enter pressed
        if send_clicked and user_input.strip():
            return user_input.strip()
        
        return None


def render_chat_sidebar() -> Dict[str, Any]:
    """
    Render chat sidebar with history and controls.
    
    Returns:
        Dict[str, Any]: Sidebar actions and data
    """
    sidebar_data = {}
    
    with st.sidebar:
        st.header("💬 Chat Controls")
        
        # Session info
        st.subheader("Current Session")
        session_id = st.session_state.get('current_session_id', 'Unknown')
        st.text(f"ID: {session_id[:8]}...")
        
        # Message count
        message_count = len(st.session_state.get('chat_history', []))
        st.metric("Messages", message_count)
        
        # Clear history button
        if st.button("🗑️ Clear History", use_container_width=True):
            sidebar_data['clear_history'] = True
        
        # Export history
        if message_count > 0:
            chat_history = ChatHistory()
            export_data = chat_history.export_history()
            st.download_button(
                "📥 Export Chat",
                export_data,
                file_name=f"chat_history_{session_id[:8]}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Search in history
        st.subheader("🔍 Search Messages")
        search_query = st.text_input("Search in chat history...")
        if search_query:
            chat_history = ChatHistory()
            matching_messages = chat_history.search_messages(search_query)
            
            if matching_messages:
                st.write(f"Found {len(matching_messages)} matches:")
                for msg in matching_messages[-5:]:  # Show last 5 matches
                    with st.expander(f"{msg.role}: {msg.content[:50]}..."):
                        st.write(msg.content)
                        st.caption(f"Time: {msg.timestamp.strftime('%H:%M:%S')}")
            else:
                st.info("No matches found")
        
        # Chat statistics
        if message_count > 0:
            st.subheader("📊 Statistics")
            messages = [ChatMessage.from_dict(msg) for msg in st.session_state.chat_history]
            
            user_messages = [msg for msg in messages if msg.role == 'user']
            assistant_messages = [msg for msg in messages if msg.role == 'assistant']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Your Messages", len(user_messages))
            with col2:
                st.metric("AI Responses", len(assistant_messages))
            
            # Average response time (if available in metadata)
            response_times = [
                msg.metadata.get('response_time', 0) 
                for msg in assistant_messages 
                if 'response_time' in msg.metadata
            ]
            
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                st.metric("Avg Response Time", f"{avg_time:.1f}s")
    
    return sidebar_data


def add_message_javascript():
    """Add JavaScript for enhanced message interactions."""
    js_code = """
    <script>
    function copyToClipboard(messageId) {
        const messageElement = document.getElementById(messageId);
        const content = messageElement.querySelector('.message-content').innerText;
        navigator.clipboard.writeText(content).then(function() {
            // Show success indication
            const btn = event.target;
            const originalText = btn.innerText;
            btn.innerText = '✅ Copied!';
            setTimeout(() => {
                btn.innerText = originalText;
            }, 2000);
        });
    }
    
    function shareMessage(messageId) {
        const messageElement = document.getElementById(messageId);
        const content = messageElement.querySelector('.message-content').innerText;
        
        if (navigator.share) {
            navigator.share({
                title: 'AI Chat Message',
                text: content
            });
        } else {
            // Fallback to copying
            navigator.clipboard.writeText(content);
            alert('Message copied to clipboard!');
        }
    }
    
    // Auto-scroll to bottom of chat
    function scrollToBottom() {
        window.scrollTo(0, document.body.scrollHeight);
    }
    
    // Call scroll function after page load
    setTimeout(scrollToBottom, 100);
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)


# Initialize styling when module is imported
load_custom_css()
