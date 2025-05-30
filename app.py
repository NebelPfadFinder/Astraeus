"""
Enhanced Streamlit App for Mistral-Qdrant Chatbot
Author: Senior Python Engineer
"""

import streamlit as st
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Optional
import uuid
import json

# Import custom services and components
from Services.mistral_service import MistralService
from Services.qdrant_service import QdrantService
from Config.settings import Settings
from Utils.ui_helpers import (
    apply_custom_css, create_message_bubble, 
    show_typing_indicator, create_sidebar
)
from Utils.logger import get_logger
from components.chat_widgets import ChatWidget, MessageRating, TypingIndicator
from components.file_uploader import FileUploader
from utils.text_processing import TextProcessor

# Initialize logger
logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Mistral AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.yourcompany.com',
        'Report a bug': 'https://github.com/yourorg/chatbot/issues',
        'About': "# Mistral-Qdrant Chatbot\nPowered by AI for intelligent conversations"
    }
)

class ChatbotApp:
    """Main application class for the Mistral-Qdrant Chatbot"""
    
    def __init__(self):
        """Initialize the chatbot application"""
        self.settings = Settings()
        self.mistral_service = None
        self.qdrant_service = None
        self.text_processor = TextProcessor()
        self.file_uploader = FileUploader()
        self.chat_widget = ChatWidget()
        
        # Initialize session state
        self._init_session_state()
        
        # Initialize services
        self._init_services()
    
    def _init_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'conversation_id' not in st.session_state:
            st.session_state.conversation_id = str(uuid.uuid4())
        
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = {}
        
        if 'current_conversation' not in st.session_state:
            st.session_state.current_conversation = st.session_state.conversation_id
        
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {
                'theme': 'auto',
                'message_density': 'normal',
                'show_timestamps': True,
                'enable_sound': False
            }
        
        if 'uploaded_documents' not in st.session_state:
            st.session_state.uploaded_documents = []
        
        if 'processing_status' not in st.session_state:
            st.session_state.processing_status = None
    
    def _init_services(self):
        """Initialize AI and database services"""
        try:
            # Initialize Mistral service
            self.mistral_service = MistralService(
                api_key=self.settings.mistral_api_key,
                model=self.settings.model_name,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens
            )
            
            # Initialize Qdrant service
            self.qdrant_service = QdrantService(
                host=self.settings.qdrant_host,
                port=self.settings.qdrant_port,
                collection_name=self.settings.collection_name
            )
            
            # Test connections
            self._test_connections()
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            st.error(f"❌ Service initialization failed: {e}")
            st.stop()
    
    def _test_connections(self):
        """Test connections to external services"""
        try:
            # Test Mistral API
            test_response = self.mistral_service.test_connection()
            if not test_response:
                st.warning("⚠️ Mistral API connection issue")
            
            # Test Qdrant connection
            qdrant_health = self.qdrant_service.health_check()
            if not qdrant_health:
                st.warning("⚠️ Qdrant database connection issue")
                
        except Exception as e:
            logger.warning(f"Connection test failed: {e}")
    
    def render_header(self):
        """Render the application header"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
                <div style='text-align: center; padding: 1rem 0;'>
                    <h1 style='margin: 0; color: #1f77b4;'>🤖 Mistral AI Chatbot</h1>
                    <p style='margin: 0.5rem 0; color: #666;'>
                        Powered by Mistral AI & Qdrant Vector Database
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the application sidebar"""
        with st.sidebar:
            st.markdown("### 🎛️ Control Panel")
            
            # Conversation management
            self._render_conversation_controls()
            
            # Document upload
            self._render_document_upload()
            
            # Settings
            self._render_settings()
            
            # Statistics
            self._render_statistics()
            
            # Help and about
            self._render_help_section()
    
    def _render_conversation_controls(self):
        """Render conversation management controls"""
        st.markdown("#### 💬 Conversations")
        
        # New conversation button
        if st.button("🆕 New Conversation", use_container_width=True):
            self._start_new_conversation()
        
        # Conversation selector
        conversation_list = list(st.session_state.conversation_history.keys())
        if conversation_list:
            selected_conv = st.selectbox(
                "Select Conversation",
                options=conversation_list,
                format_func=lambda x: f"Chat {x[:8]}..." if len(x) > 8 else f"Chat {x}",
                index=conversation_list.index(st.session_state.current_conversation) 
                if st.session_state.current_conversation in conversation_list else 0
            )
            
            if selected_conv != st.session_state.current_conversation:
                self._switch_conversation(selected_conv)
        
        # Export conversation
        if st.session_state.messages:
            if st.button("📤 Export Chat", use_container_width=True):
                self._export_conversation()
        
        # Clear conversation
        if st.button("🗑️ Clear Chat", use_container_width=True):
            self._clear_conversation()
    
    def _render_document_upload(self):
        """Render document upload section"""
        st.markdown("#### 📁 Document Upload")
        
        uploaded_files = st.file_uploader(
            "Upload documents for context",
            type=['pdf', 'txt', 'docx', 'md'],
            accept_multiple_files=True,
            help="Upload documents to provide context for your conversations"
        )
        
        if uploaded_files:
            self._process_uploaded_files(uploaded_files)
        
        # Show uploaded documents
        if st.session_state.uploaded_documents:
            st.markdown("**Uploaded Documents:**")
            for doc in st.session_state.uploaded_documents[-5:]:  # Show last 5
                st.markdown(f"• {doc['name']} ({doc['size']} chars)")
    
    def _render_settings(self):
        """Render application settings"""
        with st.expander("⚙️ Settings"):
            # Theme selection
            theme = st.selectbox(
                "Theme",
                options=['auto', 'light', 'dark'],
                index=['auto', 'light', 'dark'].index(st.session_state.user_preferences['theme'])
            )
            st.session_state.user_preferences['theme'] = theme
            
            # Message density
            density = st.selectbox(
                "Message Density",
                options=['compact', 'normal', 'spacious'],
                index=['compact', 'normal', 'spacious'].index(st.session_state.user_preferences['message_density'])
            )
            st.session_state.user_preferences['message_density'] = density
            
            # Show timestamps
            show_timestamps = st.checkbox(
                "Show Timestamps",
                value=st.session_state.user_preferences['show_timestamps']
            )
            st.session_state.user_preferences['show_timestamps'] = show_timestamps
            
            # Sound notifications
            enable_sound = st.checkbox(
                "Sound Notifications",
                value=st.session_state.user_preferences['enable_sound']
            )
            st.session_state.user_preferences['enable_sound'] = enable_sound
    
    def _render_statistics(self):
        """Render usage statistics"""
        with st.expander("📊 Statistics"):
            total_messages = len(st.session_state.messages)
            total_conversations = len(st.session_state.conversation_history)
            total_documents = len(st.session_state.uploaded_documents)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Messages", total_messages)
                st.metric("Documents", total_documents)
            with col2:
                st.metric("Conversations", total_conversations)
                st.metric("Session Time", f"{time.time() - st.session_state.get('start_time', time.time()):.0f}s")
    
    def _render_help_section(self):
        """Render help and about section"""
        with st.expander("❓ Help & About"):
            st.markdown("""
            **Quick Tips:**
            - Upload documents to provide context
            - Use @doc to reference specific documents
            - Rate responses to improve quality
            - Export conversations for later reference
            
            **Keyboard Shortcuts:**
            - Enter: Send message
            - Shift+Enter: New line
            - Ctrl+K: Focus input
            
            **Version:** 1.0.0
            """)
    
    def render_chat_interface(self):
        """Render the main chat interface"""
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat messages
            self._render_chat_messages()
            
            # Chat input
            self._render_chat_input()
    
    def _render_chat_messages(self):
        """Render chat messages with custom styling"""
        if not st.session_state.messages:
            self._show_welcome_message()
            return
        
        # Create scrollable chat area
        chat_area = st.container()
        
        with chat_area:
            for i, message in enumerate(st.session_state.messages):
                self._render_single_message(message, i)
    
    def _render_single_message(self, message: Dict, index: int):
        """Render a single chat message"""
        is_user = message['role'] == 'user'
        
        # Message container with custom styling
        message_col = st.columns([1, 4, 1] if is_user else [1, 4, 1])
        
        with message_col[1 if is_user else 1]:
            # Message bubble
            bubble_class = "user-message" if is_user else "assistant-message"
            
            # Timestamp
            timestamp = ""
            if st.session_state.user_preferences['show_timestamps']:
                msg_time = message.get('timestamp', datetime.now())
                if isinstance(msg_time, str):
                    msg_time = datetime.fromisoformat(msg_time)
                timestamp = f"<small>{msg_time.strftime('%H:%M')}</small>"
            
            # Render message with markdown
            st.markdown(f"""
                <div class="{bubble_class}">
                    {message['content']}
                    {timestamp}
                </div>
            """, unsafe_allow_html=True)
            
            # Message actions (for assistant messages)
            if not is_user:
                col1, col2, col3, col4 = st.columns([1, 1, 1, 6])
                
                with col1:
                    if st.button("👍", key=f"like_{index}", help="Good response"):
                        self._rate_message(index, 1)
                
                with col2:
                    if st.button("👎", key=f"dislike_{index}", help="Poor response"):
                        self._rate_message(index, -1)
                
                with col3:
                    if st.button("📋", key=f"copy_{index}", help="Copy to clipboard"):
                        st.write("Copied to clipboard!")  # JavaScript would handle actual copying
    
    def _render_chat_input(self):
        """Render the chat input area"""
        # Input container
        input_container = st.container()
        
        with input_container:
            col1, col2 = st.columns([6, 1])
            
            with col1:
                user_input = st.text_area(
                    "Type your message...",
                    height=100,
                    placeholder="Ask me anything! Upload documents first for context-aware responses.",
                    key="chat_input",
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                send_button = st.button("Send 📤", use_container_width=True, type="primary")
                
                # Advanced options
                with st.expander("🔧 Options"):
                    use_context = st.checkbox("Use document context", value=True)
                    temperature = st.slider("Creativity", 0.0, 1.0, 0.7, 0.1)
                    max_tokens = st.number_input("Max tokens", 100, 2000, 1000)
            
            # Handle message sending
            if send_button and user_input.strip():
                self._send_message(user_input, use_context, temperature, max_tokens)
                st.rerun()
    
    def _send_message(self, user_input: str, use_context: bool, temperature: float, max_tokens: int):
        """Send a message and get AI response"""
        try:
            # Add user message
            user_message = {
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            }
            st.session_state.messages.append(user_message)
            
            # Show typing indicator
            with st.spinner("🤖 Thinking..."):
                # Get context if requested
                context = ""
                if use_context and st.session_state.uploaded_documents:
                    context = self._get_relevant_context(user_input)
                
                # Generate response
                response = self.mistral_service.generate_response(
                    messages=st.session_state.messages,
                    context=context,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Add assistant message
                assistant_message = {
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat(),
                    'context_used': bool(context)
                }
                st.session_state.messages.append(assistant_message)
                
                # Save conversation
                self._save_conversation()
                
                # Clear input
                st.session_state.chat_input = ""
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            st.error(f"❌ Error: {e}")
    
    def _get_relevant_context(self, query: str) -> str:
        """Retrieve relevant context from uploaded documents"""
        try:
            # Generate query embedding
            query_vector = self.mistral_service.create_embedding(query)
            
            # Search for relevant documents
            results = self.qdrant_service.search_similar(query_vector, limit=3)
            
            # Format context
            context_parts = []
            for result in results:
                context_parts.append(f"[{result['metadata']['filename']}]: {result['content']}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return ""
    
    def _process_uploaded_files(self, uploaded_files):
        """Process uploaded files and add to vector database"""
        try:
            with st.spinner("Processing uploaded files..."):
                for uploaded_file in uploaded_files:
                    # Check if already processed
                    if any(doc['name'] == uploaded_file.name for doc in st.session_state.uploaded_documents):
                        continue
                    
                    # Extract text
                    text_content = self.file_uploader.extract_text(uploaded_file)
                    
                    # Process and chunk text
                    chunks = self.text_processor.chunk_text(text_content)
                    
                    # Add to vector database
                    for i, chunk in enumerate(chunks):
                        self.qdrant_service.add_document(
                            text=chunk,
                            metadata={
                                'filename': uploaded_file.name,
                                'chunk_id': i,
                                'upload_date': datetime.now().isoformat()
                            }
                        )
                    
                    # Track uploaded document
                    st.session_state.uploaded_documents.append({
                        'name': uploaded_file.name,
                        'size': len(text_content),
                        'chunks': len(chunks),
                        'upload_date': datetime.now().isoformat()
                    })
                
                st.success(f"✅ Processed {len(uploaded_files)} file(s)")
                
        except Exception as e:
            logger.error(f"Error processing files: {e}")
            st.error(f"❌ Error processing files: {e}")
    
    def _show_welcome_message(self):
        """Show welcome message when no chat history exists"""
        st.markdown("""
            <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;'>
                <h2>👋 Welcome to Mistral AI Chatbot!</h2>
                <p>I'm here to help you with any questions or tasks. You can:</p>
                <ul style='text-align: left; display: inline-block;'>
                    <li>Ask me anything - I'm powered by advanced AI</li>
                    <li>Upload documents for context-aware conversations</li>
                    <li>Export your chat history for reference</li>
                    <li>Customize the interface to your preferences</li>
                </ul>
                <p><strong>Start by typing a message below! 🚀</strong></p>
            </div>
        """, unsafe_allow_html=True)
    
    def _start_new_conversation(self):
        """Start a new conversation"""
        # Save current conversation
        if st.session_state.messages:
            self._save_conversation()
        
        # Create new conversation
        new_id = str(uuid.uuid4())
        st.session_state.conversation_id = new_id
        st.session_state.current_conversation = new_id
        st.session_state.messages = []
        
        st.rerun()
    
    def _switch_conversation(self, conversation_id: str):
        """Switch to a different conversation"""
        # Save current conversation
        if st.session_state.messages:
            self._save_conversation()
        
        # Load selected conversation
        st.session_state.current_conversation = conversation_id
        st.session_state.messages = st.session_state.conversation_history.get(conversation_id, [])
        
        st.rerun()
    
    def _save_conversation(self):
        """Save current conversation to history"""
        if st.session_state.messages:
            st.session_state.conversation_history[st.session_state.conversation_id] = st.session_state.messages.copy()
    
    def _clear_conversation(self):
        """Clear current conversation"""
        st.session_state.messages = []
        st.rerun()
    
    def _export_conversation(self):
        """Export conversation to JSON"""
        try:
            conversation_data = {
                'conversation_id': st.session_state.conversation_id,
                'messages': st.session_state.messages,
                'export_date': datetime.now().isoformat(),
                'total_messages': len(st.session_state.messages)
            }
            
            json_data = json.dumps(conversation_data, indent=2)
            
            st.download_button(
                label="Download Conversation",
                data=json_data,
                file_name=f"conversation_{st.session_state.conversation_id[:8]}.json",
                mime="application/json"
            )
            
        except Exception as e:
            logger.error(f"Error exporting conversation: {e}")
            st.error(f"❌ Export failed: {e}")
    
    def _rate_message(self, message_index: int, rating: int):
        """Rate a message for quality feedback"""
        try:
            if 0 <= message_index < len(st.session_state.messages):
                st.session_state.messages[message_index]['rating'] = rating
                st.success("👍 Thanks for your feedback!" if rating > 0 else "👎 Feedback noted, we'll improve!")
                
        except Exception as e:
            logger.error(f"Error rating message: {e}")
    
    def run(self):
        """Run the main application"""
        try:
            # Apply custom CSS
            apply_custom_css()
            
            # Render components
            self.render_header()
            self.render_sidebar()
            self.render_chat_interface()
            
            # Initialize start time
            if 'start_time' not in st.session_state:
                st.session_state.start_time = time.time()
                
        except Exception as e:
            logger.error(f"Application error: {e}")
            st.error(f"❌ Application error: {e}")
            st.stop()

def main():
    """Main entry point"""
    try:
        app = ChatbotApp()
        app.run()
    except Exception as e:
        st.error(f"❌ Failed to start application: {e}")
        logger.error(f"Startup error: {e}")

if __name__ == "__main__":
    main()
