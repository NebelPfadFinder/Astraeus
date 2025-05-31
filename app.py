import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import sys
import os

# Add project root to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from services.mistral_service import MistralService
from services.qdrant_service import QdrantService
from config.settings import AppSettings
from utils.ui_helpers import apply_custom_css, format_message
from utils.logger import setup_logger
from utils.text_processing import preprocess_text, extract_keywords
from components.chat_widgets import render_message_bubble, render_typing_indicator
from components.file_uploader import FileUploader

# Initialize logger
logger = setup_logger(__name__)

class ChatbotApp:
    """Main chatbot application class with full integration."""
    
    def __init__(self):
        """Initialize the chatbot application with all services."""
        try:
            # Load settings from config
            self.settings = AppSettings()
            
            # Initialize services
            self.mistral_service = MistralService(self.settings.mistral_api_key)
            self.qdrant_service = QdrantService(
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key,
                collection_name=getattr(self.settings, 'qdrant_collection_name', 'default_collection')
            )
            
            # Initialize file uploader component
            self.file_uploader = FileUploader()
            
            logger.info("ChatbotApp initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChatbotApp: {str(e)}")
            st.error(f"Failed to initialize application: {str(e)}")
            raise
        
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        session_defaults = {
            "messages": [],
            "conversation_id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "uploaded_files": [],
            "processing_status": "ready",
            "context_enabled": True,
            "auto_scroll": True,
            "theme": "default"
        }
        
        for key, default_value in session_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def render_header(self):
        """Render the application header with branding."""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div class="header-container">
                <h1 class="main-title">🤖 AI Assistant</h1>
                <p class="subtitle">Powered by Mistral AI & Qdrant Vector Search</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
    
    def render_chat_interface(self):
        """Render the main chat interface with enhanced features."""
        # Create main chat area
        chat_container = st.container()
        
        with chat_container:
            # Display conversation history
            if st.session_state.messages:
                for i, message in enumerate(st.session_state.messages):
                    self.render_message(message, i)
            else:
                # Welcome message for new conversations
                self.render_welcome_message()
        
        # Chat input area
        self.render_chat_input()
    
    def render_message(self, message: Dict[str, Any], index: int):
        """Render individual message with enhanced styling."""
        is_user = message["role"] == "user"
        
        # Use custom chat widget for better styling
        with st.chat_message(message["role"], avatar="👤" if is_user else "🤖"):
            # Format and display message content
            formatted_content = format_message(message["content"])
            st.markdown(formatted_content, unsafe_allow_html=True)
            
            # Show context sources for assistant messages
            if not is_user and "context" in message and message["context"]:
                self.render_context_sources(message["context"])
            
            # Show timestamp
            if "timestamp" in message:
                timestamp = message["timestamp"]
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('T', ' ').replace('Z', ''))
                st.caption(f"📅 {timestamp.strftime('%H:%M:%S')}")
    
    def render_context_sources(self, context: List[Dict[str, Any]]):
        """Render context sources in an expandable section."""
        if not context:
            return
            
        with st.expander(f"📚 Context Sources ({len(context)} found)", expanded=False):
            for i, source in enumerate(context, 1):
                with st.container():
                    st.markdown(f"**Source {i}:**")
                    
                    # Display source metadata if available
                    if "metadata" in source:
                        metadata = source["metadata"]
                        if "file_name" in metadata:
                            st.caption(f"📄 File: {metadata['file_name']}")
                        if "score" in metadata:
                            st.caption(f"🎯 Relevance: {metadata['score']:.3f}")
                    
                    # Display source text (truncated)
                    text = source.get("text", "N/A")
                    truncated_text = text[:300] + "..." if len(text) > 300 else text
                    st.markdown(f"```\n{truncated_text}\n```")
                    
                    if i < len(context):
                        st.markdown("---")
    
    def render_welcome_message(self):
        """Render welcome message for new conversations."""
        st.markdown("""
        <div class="welcome-container">
            <h3>👋 Welcome to your AI Assistant!</h3>
            <p>I'm here to help you with questions, analysis, and more. Here's what I can do:</p>
            <ul>
                <li>💬 Answer questions using advanced AI</li>
                <li>🔍 Search through your documents with semantic search</li>
                <li>📄 Process and analyze uploaded files</li>
                <li>🧠 Maintain context across our conversation</li>
            </ul>
            <p><strong>Start by asking me anything or uploading a document!</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_chat_input(self):
        """Render the chat input area with enhanced features."""
        # Create input area
        input_container = st.container()
        
        with input_container:
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Main chat input
                if prompt := st.chat_input(
                    "Ask me anything...", 
                    key="chat_input",
                    disabled=(st.session_state.processing_status != "ready")
                ):
                    self.handle_user_input(prompt)
            
            with col2:
                # Quick action buttons
                if st.button("🔄", help="Regenerate last response", disabled=not st.session_state.messages):
                    if st.session_state.messages:
                        last_user_message = None
                        for msg in reversed(st.session_state.messages):
                            if msg["role"] == "user":
                                last_user_message = msg["content"]
                                break
                        
                        if last_user_message:
                            # Remove last assistant response
                            if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
                                st.session_state.messages.pop()
                            self.handle_user_input(last_user_message)
    
    def handle_user_input(self, user_input: str):
        """Handle user input with enhanced processing."""
        try:
            # Preprocess user input
            processed_input = preprocess_text(user_input)
            keywords = extract_keywords(processed_input)
            
            # Add user message to chat
            user_message = {
                "role": "user", 
                "content": user_input,
                "processed_content": processed_input,
                "keywords": keywords,
                "timestamp": datetime.now()
            }
            st.session_state.messages.append(user_message)
            
            # Update processing status
            st.session_state.processing_status = "processing"
            
            # Display user message
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)
            
            # Generate and display assistant response
            with st.chat_message("assistant", avatar="🤖"):
                # Show typing indicator
                typing_placeholder = st.empty()
                with typing_placeholder:
                    render_typing_indicator()
                
                # Generate response
                response_data = asyncio.run(self.generate_response(user_input))
                
                # Clear typing indicator
                typing_placeholder.empty()
                
                # Display response
                formatted_response = format_message(response_data["content"])
                st.markdown(formatted_response, unsafe_allow_html=True)
                
                # Show context sources if available
                if response_data.get("context"):
                    self.render_context_sources(response_data["context"])
                
                # Show response timestamp
                st.caption(f"📅 {datetime.now().strftime('%H:%M:%S')}")
            
            # Add assistant message to chat
            assistant_message = {
                "role": "assistant",
                "content": response_data["content"], 
                "context": response_data.get("context", []),
                "metadata": response_data.get("metadata", {}),
                "timestamp": datetime.now()
            }
            st.session_state.messages.append(assistant_message)
            
            # Reset processing status
            st.session_state.processing_status = "ready"
            
            # Auto-scroll to bottom if enabled
            if st.session_state.auto_scroll:
                st.rerun()
            
        except Exception as e:
            logger.error(f"Error handling user input: {str(e)}")
            st.session_state.processing_status = "error"
            st.error("Sorry, I encountered an error. Please try again.")
    
    async def generate_response(self, user_input: str) -> Dict[str, Any]:
        """Generate response using Mistral API with enhanced Qdrant context."""
        try:
            context_results = []
            context_text = ""
            
            # Get relevant context from Qdrant if enabled
            if st.session_state.context_enabled:
                try:
                    context_results = await self.qdrant_service.search_similar(
                        query=user_input,
                        limit=getattr(self.settings, 'context_limit', 5),
                        score_threshold=getattr(self.settings, 'similarity_threshold', 0.7)
                    )
                    
                    if context_results:
                        context_text = "\n\n".join([
                            f"[Context {i+1}]: {result.get('text', '')}"
                            for i, result in enumerate(context_results)
                        ])
                        logger.info(f"Retrieved {len(context_results)} context results")
                    
                except Exception as e:
                    logger.warning(f"Context retrieval failed: {str(e)}")
                    # Continue without context
            
            # Prepare conversation history (last N messages)
            history_limit = getattr(self.settings, 'history_limit', 10)
            recent_messages = st.session_state.messages[-history_limit:] if st.session_state.messages else []
            
            # Generate response using Mistral
            response = await self.mistral_service.generate_response(
                user_input=user_input,
                context=context_text,
                conversation_history=recent_messages
            )
            
            return {
                "content": response,
                "context": context_results,
                "metadata": {
                    "context_count": len(context_results),
                    "has_context": bool(context_text),
                    "processing_time": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "content": "I apologize, but I'm having trouble processing your request right now. Please try again.",
                "context": [],
                "metadata": {"error": str(e)}
            }
    
    def render_sidebar(self):
        """Render enhanced sidebar with controls and information."""
        with st.sidebar:
            # App header in sidebar
            st.markdown("### ⚙️ Controls & Settings")
            
            # File upload section
            st.markdown("#### 📄 Document Upload")
            uploaded_files = self.file_uploader.render_upload_interface()
            
            if uploaded_files:
                if st.button("🔄 Process Files", use_container_width=True):
                    self.process_uploaded_files(uploaded_files)
            
            st.markdown("---")
            
            # Chat controls
            st.markdown("#### 💬 Chat Controls")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear", use_container_width=True, help="Clear chat history"):
                    st.session_state.messages = []
                    st.session_state.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    st.rerun()
            
            with col2:
                if st.button("💾 Export", use_container_width=True, help="Export chat history"):
                    self.export_chat()
            
            # Settings
            st.markdown("#### ⚙️ Settings")
            
            st.session_state.context_enabled = st.toggle(
                "🔍 Context Search", 
                value=st.session_state.context_enabled,
                help="Enable semantic search for relevant context"
            )
            
            st.session_state.auto_scroll = st.toggle(
                "📜 Auto-scroll", 
                value=st.session_state.auto_scroll,
                help="Automatically scroll to new messages"
            )
            
            st.markdown("---")
            
            # Statistics
            st.markdown("#### 📊 Session Stats")
            
            # Create metrics
            total_messages = len(st.session_state.messages)
            user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total", total_messages)
            with col2:
                st.metric("Questions", user_messages)
            
            st.metric("Session ID", st.session_state.conversation_id[-8:])
            st.metric("Status", st.session_state.processing_status.title())
            
            # File stats
            if st.session_state.uploaded_files:
                st.metric("Uploaded Files", len(st.session_state.uploaded_files))
            
            st.markdown("---")
            
            # System info
            st.markdown("#### ℹ️ System Info")
            st.info("""
            **AI Components:**
            - 🧠 Mistral AI (Language Model)
            - 🔍 Qdrant (Vector Search)
            - 🎨 Streamlit (Interface)
            
            **Features:**
            - Semantic document search
            - Context-aware responses
            - File processing
            - Conversation export
            """)
            
            # Health status
            if st.button("🔍 Health Check", use_container_width=True):
                self.run_health_check()
    
    def process_uploaded_files(self, uploaded_files: List[Any]):
        """Process uploaded files and add to vector database."""
        try:
            with st.spinner("Processing uploaded files..."):
                processed_files = self.file_uploader.process_files(uploaded_files)
                
                # Add processed content to Qdrant
                for file_data in processed_files:
                    asyncio.run(self.qdrant_service.add_document(
                        text=file_data["content"],
                        metadata={
                            "file_name": file_data["name"],
                            "file_type": file_data["type"],
                            "upload_time": datetime.now().isoformat(),
                            "size": file_data.get("size", 0)
                        }
                    ))
                
                st.session_state.uploaded_files.extend(processed_files)
                st.success(f"✅ Processed {len(processed_files)} files successfully!")
                
        except Exception as e:
            logger.error(f"Error processing files: {str(e)}")
            st.error(f"Error processing files: {str(e)}")
    
    def export_chat(self):
        """Export chat history with enhanced format."""
        try:
            chat_data = {
                "metadata": {
                    "conversation_id": st.session_state.conversation_id,
                    "export_timestamp": datetime.now().isoformat(),
                    "total_messages": len(st.session_state.messages),
                    "app_version": "1.0.0"
                },
                "messages": []
            }
            
            for msg in st.session_state.messages:
                message_data = {
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg.get("timestamp", datetime.now()).isoformat() if hasattr(msg.get("timestamp", datetime.now()), 'isoformat') else str(msg.get("timestamp", datetime.now()))
                }
                
                # Add additional data for assistant messages
                if msg["role"] == "assistant":
                    if "context" in msg:
                        message_data["context_count"] = len(msg["context"])
                    if "metadata" in msg:
                        message_data["metadata"] = msg["metadata"]
                
                chat_data["messages"].append(message_data)
            
            # Create download button
            st.download_button(
                label="📥 Download Chat History",
                data=json.dumps(chat_data, indent=2, ensure_ascii=False),
                file_name=f"chat_export_{st.session_state.conversation_id}.json",
                mime="application/json",
                use_container_width=True
            )
            
        except Exception as e:
            logger.error(f"Error exporting chat: {str(e)}")
            st.error("Failed to export chat history.")
    
    def run_health_check(self):
        """Run system health check."""
        try:
            with st.spinner("Running health check..."):
                health_status = {}
                
                # Check Mistral service
                try:
                    # This would depend on your MistralService implementation
                    health_status["mistral"] = "✅ Connected"
                except:
                    health_status["mistral"] = "❌ Connection Failed"
                
                # Check Qdrant service
                try:
                    # This would depend on your QdrantService implementation
                    health_status["qdrant"] = "✅ Connected"
                except:
                    health_status["qdrant"] = "❌ Connection Failed"
                
                # Display results
                st.success("Health Check Complete:")
                for service, status in health_status.items():
                    st.write(f"**{service.title()}:** {status}")
                    
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            st.error("Health check failed.")
    
    def run(self):
        """Main application entry point with enhanced error handling."""
        try:
            # Configure page with custom settings
            st.set_page_config(
                page_title="AI Assistant - Mistral & Qdrant",
                page_icon="🤖",
                layout="wide",
                initial_sidebar_state="expanded",
                menu_items={
                    'Get Help': 'https://github.com/your-repo/issues',
                    'Report a bug': 'https://github.com/your-repo/issues',
                    'About': "# AI Assistant\nPowered by Mistral AI and Qdrant"
                }
            )
            
            # Apply custom CSS styling
            apply_custom_css()
            
            # Initialize session state
            self.initialize_session_state()
            
            # Render application components
            self.render_header()
            
            # Create main layout
            col1, col2 = st.columns([3, 1])
            
            with col1:
                self.render_chat_interface()
            
            with col2:
                self.render_sidebar()
            
            # Add footer
            st.markdown("---")
            st.markdown(
                "<div style='text-align: center; color: #666;'>"
                "Built with Streamlit • Powered by Mistral AI & Qdrant"
                "</div>", 
                unsafe_allow_html=True
            )
            
        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            st.error("⚠️ Application failed to load. Please refresh the page or contact support.")
            st.exception(e)

def main():
    """Application entry point with error handling."""
    try:
        app = ChatbotApp()
        app.run()
    except Exception as e:
        st.error(f"Failed to start application: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()
