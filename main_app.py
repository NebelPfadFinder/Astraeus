"""
Complete Streamlit Chatbot Application
Modern chatbot interface with Mistral API and Qdrant integration
"""

import streamlit as st
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
import json
import os
from dataclasses import dataclass

# Import the UI components
from ui_components import ModernChatUI, ChatMessage, ChatHistory, initialize_chat_ui, initialize_chat_history

# Configuration
@dataclass
class AppConfig:
    """Application configuration"""
    page_title: str = "Modern AI Chatbot"
    page_icon: str = "🤖"
    layout: str = "wide"
    mistral_model: str = "mistral-large-latest"
    max_tokens: int = 1024
    temperature: float = 0.7
    qdrant_collection: str = "knowledge_base"


class MistralChatBot:
    """Mistral AI chatbot with Qdrant integration"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.mistral_client = None
        self.qdrant_client = None
        self.is_connected = False
        self.setup_clients()
    
    def setup_clients(self):
        """Initialize Mistral and Qdrant clients"""
        try:
            # Initialize Mistral client
            mistral_api_key = os.getenv('MISTRAL_API_KEY')
            if mistral_api_key:
                # Add your Mistral client initialization here
                # self.mistral_client = MistralClient(api_key=mistral_api_key)
                pass
            
            # Initialize Qdrant client
            qdrant_url = os.getenv('QDRANT_URL', 'localhost')
            qdrant_port = os.getenv('QDRANT_PORT', 6333)
            # Add your Qdrant client initialization here
            # self.qdrant_client = QdrantClient(host=qdrant_url, port=qdrant_port)
            
            self.is_connected = True
        except Exception as e:
            st.error(f"Failed to initialize clients: {str(e)}")
            self.is_connected = False
    
    async def get_context_from_qdrant(self, query: str, limit: int = 3) -> List[Dict]:
        """Retrieve relevant context from Qdrant vector database"""
        # Placeholder for Qdrant search implementation
        # In a real implementation, you would:
        # 1. Encode the query using your embedding model
        # 2. Search the Qdrant collection
        # 3. Return relevant documents
        
        return [
            {"text": "Sample context 1", "score": 0.95},
            {"text": "Sample context 2", "score": 0.87},
        ]
    
    async def generate_response(self, message: str, context: List[Dict] = None) -> str:
        """Generate response using Mistral API"""
        # Placeholder for Mistral API call
        # In a real implementation, you would:
        # 1. Prepare the prompt with context
        # 2. Call Mistral API
        # 3. Return the generated response
        
        await asyncio.sleep(1)  # Simulate API call delay
        return f"This is a simulated response to: {message}"
    
    def get_system_status(self) -> Dict[str, bool]:
        """Get system connection status"""
        return {
            'mistral': self.mistral_client is not None,
            'qdrant': self.qdrant_client is not None
        }


def setup_page_config():
    """Configure Streamlit page"""
    config = AppConfig()
    st.set_page_config(
        page_title=config.page_title,
        page_icon=config.page_icon,
        layout=config.layout,
        initial_sidebar_state="expanded"
    )
    return config


def render_header(ui: ModernChatUI, bot: MistralChatBot):
    """Render the application header"""
    st.markdown("""
    <div class="chat-container">
        <h1 style="text-align: center; color: #1e3a5f; margin: 0;">
            🤖 Modern AI Chatbot
        </h1>
        <p style="text-align: center; color: #5a6c7d; margin: 8px 0 0 0;">
            Powered by Mistral AI & Qdrant Vector Database
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display system status
    status = bot.get_system_status()
    ui.display_system_status(status['mistral'], status['qdrant'])


def render_sidebar(ui: ModernChatUI, history: ChatHistory):
    """Render the sidebar with controls and information"""
    st.sidebar.title("🎛️ Controls")
    
    # Chat settings
    ui.render_sidebar_section(
        "Chat Settings",
        """
        <div>
            <p><strong>Model:</strong> Mistral Large</p>
            <p><strong>Temperature:</strong> 0.7</p>
            <p><strong>Max Tokens:</strong> 1024</p>
        </div>
        """
    )
    
    # Quick actions
    st.sidebar.subheader("🚀 Quick Actions")
    quick_actions = [
        "Explain quantum computing",
        "Write a Python function",
        "Summarize recent news",
        "Help with coding",
        "Creative writing prompt"
    ]
    
    for action in quick_actions:
        if st.sidebar.button(action, key=f"quick_{action}"):
            return action
    
    # Chat history controls
    st.sidebar.subheader("📚 Chat History")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("Clear History", key="clear_history"):
            history.clear_history()
            st.rerun()
    
    with col2:
        if st.button("Export Chat", key="export_chat"):
            return "export"
    
    # Statistics
    ui.render_sidebar_section(
        "Statistics",
        f"""
        <div>
            <p><strong>Messages:</strong> {len(history.messages)}</p>
            <p><strong>Session Duration:</strong> {get_session_duration()}</p>
            <p><strong>Status:</strong> <span style="color: #8faa6f;">Online</span></p>
        </div>
        """
    )
    
    return None


def get_session_duration() -> str:
    """Get session duration"""
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()
    
    duration = datetime.now() - st.session_state.session_start
    minutes = int(duration.total_seconds() / 60)
    return f"{minutes}m"


def render_chat_messages(ui: ModernChatUI, history: ChatHistory):
    """Render chat messages"""
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not history.messages:
        # Welcome message
        welcome_msg = ui.create_message_bubble(
            "Hello! I'm your AI assistant powered by Mistral AI. How can I help you today?",
            "bot"
        )
        st.markdown(welcome_msg, unsafe_allow_html=True)
    else:
        # Render all messages
        for message in history.messages:
            bubble = ui.create_message_bubble(
                message.content,
                message.sender,
                message.timestamp
            )
            st.markdown(bubble, unsafe_allow_html=True)
    
    # Show typing indicator if bot is responding
    if st.session_state.get('bot_typing', False):
        typing_indicator = ui.create_typing_indicator()
        st.markdown(typing_indicator, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def handle_user_input(ui: ModernChatUI, history: ChatHistory, bot: MistralChatBot):
    """Handle user input and generate response"""
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to history
        user_message = ChatMessage(content=user_input, sender="user")
        history.add_message(user_message)
        
        # Show typing indicator
        st.session_state.bot_typing = True
        st.session_state.processing_response = True
        st.rerun()


async def process_bot_response(user_input: str, bot: MistralChatBot, history: ChatHistory, ui: ModernChatUI):
    """Process bot response asynchronously"""
    try:
        # Get context from Qdrant
        context = await bot.get_context_from_qdrant(user_input)
        
        # Generate response
        response = await bot.generate_response(user_input, context)
        
        # Add bot response to history
        bot_message = ChatMessage(
            content=response,
            sender="bot",
            metadata={"context_used": len(context)}
        )
        history.add_message(bot_message)
        
        # Hide typing indicator
        st.session_state.bot_typing = False
        
        return response
        
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        st.session_state.bot_typing = False
        return None


def handle_quick_action(action: str, history: ChatHistory):
    """Handle quick action selection"""
    if action:
        user_message = ChatMessage(content=action, sender="user")
        history.add_message(user_message)
        st.session_state.bot_typing = True
        st.session_state.processing_response = True
        st.rerun()


def main():
    """Main application function"""
    # Setup and initialize session state FIRST
    config = setup_page_config()
    initialize_session()  # Move this up before any other initialization
    
    ui = initialize_chat_ui()
    history = initialize_chat_history()
    bot = MistralChatBot(config)
    
    # Render UI
    render_header(ui, bot)
    
    # Sidebar
    sidebar_action = render_sidebar(ui, history)
    
    # Handle sidebar actions
    if sidebar_action == "export":
        st.download_button(
            label="Download Chat History",
            data=history.export_history(),
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    elif sidebar_action and sidebar_action != "export":
        handle_quick_action(sidebar_action, history)
    
    # Main chat area
    render_chat_messages(ui, history)
    
    # Handle user input
    handle_user_input(ui, history, bot)
    
    # Process pending bot response
    if st.session_state.get('bot_typing', False) and history.messages:
        last_message = history.messages[-1]
        if last_message.sender == "user" and not st.session_state.get('processing_response', False):
            # Prevent multiple processing
            st.session_state.processing_response = True
            
            # Run async bot response
            with st.spinner("AI is thinking..."):
                try:
                    # Simulate async call
                    time.sleep(2)  # Replace with actual async call
                    response = f"Thank you for your message: '{last_message.content}'. This is a simulated response from the AI assistant."
                    
                    bot_message = ChatMessage(
                        content=response,
                        sender="bot",
                        metadata={"processing_time": 2.0}
                    )
                    history.add_message(bot_message)
                    st.session_state.bot_typing = False
                    st.session_state.processing_response = False
                    st.rerun()
                    
                except Exception as e:
                    ui.show_notification(f"Error: {str(e)}", "error")
                    st.session_state.bot_typing = False
                    st.session_state.processing_response = False
    
    # Quick actions below chat
    st.markdown("---")
    st.subheader("💡 Quick Actions")
    
    quick_actions = [
        "What can you help me with?",
        "Explain a complex topic",
        "Help me write code",
        "Creative writing assistance",
        "Data analysis help"
    ]
    
    quick_actions_html = ui.render_quick_actions(quick_actions)
    st.markdown(quick_actions_html, unsafe_allow_html=True)
    
    # Handle quick action clicks (alternative method using buttons)
    cols = st.columns(len(quick_actions))
    for i, action in enumerate(quick_actions):
        with cols[i]:
            if st.button(action, key=f"qa_{i}", use_container_width=True):
                handle_quick_action(action, history)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #5a6c7d; padding: 20px;">
        <p>Built with ❤️ using Streamlit, Mistral AI, and Qdrant</p>
        <p style="font-size: 12px;">Session ID: {session_id} | Uptime: {uptime}</p>
    </div>
    """.format(
        session_id=st.session_state.get('session_id', 'unknown'),
        uptime=get_session_duration()
    ), unsafe_allow_html=True)


class AdvancedFeatures:
    """Advanced features for the chatbot"""
    
    @staticmethod
    def setup_file_upload(ui: ModernChatUI):
        """Setup file upload functionality"""
        st.sidebar.subheader("📎 File Upload")
        uploaded_file = st.sidebar.file_uploader(
            "Upload a document",
            type=['txt', 'pdf', 'docx', 'csv'],
            help="Upload a file to add to the knowledge base"
        )
        
        if uploaded_file:
            with st.spinner("Processing file..."):
                # Process file and add to Qdrant
                ui.show_notification(f"File '{uploaded_file.name}' uploaded successfully!", "success")
                return uploaded_file.name
        return None
    
    @staticmethod
    def setup_conversation_modes(history: ChatHistory):
        """Setup different conversation modes"""
        st.sidebar.subheader("🎭 Conversation Mode")
        
        modes = {
            "🤖 Assistant": "Helpful AI assistant",
            "👨‍💻 Code Helper": "Focus on programming and technical help",
            "✍️ Creative Writer": "Creative writing and storytelling",
            "📊 Data Analyst": "Data analysis and insights",
            "🎓 Tutor": "Educational explanations and learning"
        }
        
        selected_mode = st.sidebar.selectbox(
            "Choose conversation style:",
            options=list(modes.keys()),
            format_func=lambda x: x,
            help="Select how the AI should behave"
        )
        
        st.sidebar.info(modes[selected_mode])
        return selected_mode
    
    @staticmethod
    def setup_advanced_settings():
        """Setup advanced configuration options"""
        with st.sidebar.expander("⚙️ Advanced Settings"):
            temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
            max_tokens = st.slider("Max Tokens", 100, 2000, 1024, 50)
            top_p = st.slider("Top P", 0.1, 1.0, 0.9, 0.1)
            
            # Context settings
            st.subheader("Context Settings")
            max_context_docs = st.slider("Max Context Documents", 1, 10, 3)
            context_threshold = st.slider("Context Relevance Threshold", 0.0, 1.0, 0.7, 0.05)
            
            return {
                'temperature': temperature,
                'max_tokens': max_tokens,
                'top_p': top_p,
                'max_context_docs': max_context_docs,
                'context_threshold': context_threshold
            }


def initialize_session():
    """Initialize session state variables"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"chat_{int(time.time())}"
    
    if 'bot_typing' not in st.session_state:
        st.session_state.bot_typing = False
    
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()
    
    if 'conversation_mode' not in st.session_state:
        st.session_state.conversation_mode = "🤖 Assistant"
    
    if 'advanced_settings' not in st.session_state:
        st.session_state.advanced_settings = {
            'temperature': 0.7,
            'max_tokens': 1024,
            'top_p': 0.9,
            'max_context_docs': 3,
            'context_threshold': 0.7
        }
    
    if 'processing_response' not in st.session_state:
        st.session_state.processing_response = False


def enhanced_main():
    """Enhanced main function with advanced features"""
    # Setup and initialize session state FIRST
    config = setup_page_config()
    initialize_session()  # Initialize session state before anything else
    
    ui = initialize_chat_ui()
    history = initialize_chat_history()
    bot = MistralChatBot(config)
    
    # Advanced features
    features = AdvancedFeatures()
    
    # Render UI
    render_header(ui, bot)
    
    # Enhanced sidebar
    uploaded_file = features.setup_file_upload(ui)
    conversation_mode = features.setup_conversation_modes(history)
    advanced_settings = features.setup_advanced_settings()
    
    # Update session state
    st.session_state.conversation_mode = conversation_mode
    st.session_state.advanced_settings = advanced_settings
    
    # Regular sidebar content
    sidebar_action = render_sidebar(ui, history)
    
    # Handle file upload
    if uploaded_file:
        ui.show_notification(f"Processing {uploaded_file}...", "info")
    
    # Main application flow
    if sidebar_action == "export":
        st.download_button(
            label="Download Chat History",
            data=history.export_history(),
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    elif sidebar_action and sidebar_action != "export":
        handle_quick_action(sidebar_action, history)
    
    # Chat interface
    render_chat_messages(ui, history)
    handle_user_input(ui, history, bot)
    
    # Process bot responses
    if st.session_state.get('bot_typing', False) and history.messages:
        last_message = history.messages[-1]
        if last_message.sender == "user" and not st.session_state.get('processing_response', False):
            # Prevent multiple processing
            st.session_state.processing_response = True
            
            with st.spinner("AI is thinking..."):
                try:
                    time.sleep(2)
                    
                    # Customize response based on conversation mode
                    mode_prefix = {
                        "🤖 Assistant": "As your AI assistant, ",
                        "👨‍💻 Code Helper": "From a programming perspective, ",
                        "✍️ Creative Writer": "Let me craft a creative response: ",
                        "📊 Data Analyst": "Analyzing your request: ",
                        "🎓 Tutor": "Let me explain this step by step: "
                    }
                    
                    prefix = mode_prefix.get(conversation_mode, "")
                    response = f"{prefix}Thank you for your message: '{last_message.content}'. This is a simulated response tailored to {conversation_mode} mode."
                    
                    bot_message = ChatMessage(
                        content=response,
                        sender="bot",
                        metadata={
                            "mode": conversation_mode,
                            "settings": advanced_settings,
                            "processing_time": 2.0
                        }
                    )
                    history.add_message(bot_message)
                    st.session_state.bot_typing = False
                    st.session_state.processing_response = False
                    st.rerun()
                    
                except Exception as e:
                    ui.show_notification(f"Error: {str(e)}", "error")
                    st.session_state.bot_typing = False
                    st.session_state.processing_response = False
    
    # Footer with enhanced info
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Messages", len(history.messages))
    
    with col2:
        st.metric("Session Time", get_session_duration())
    
    with col3:
        st.metric("Mode", conversation_mode.split()[1])


if __name__ == "__main__":
    # Choose which main function to run
    # main()  # Basic version
    enhanced_main()  # Enhanced version with advanced features
