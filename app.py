# streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false
import streamlit as st
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import logging

from services.mistral_service import MistralService
from services.qdrant_service import QdrantService
from config.settings import *
from utils.ui_helpers import *
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

class ChatbotApp:
    """Main chatbot application class."""
    
    def __init__(self):
        self.settings = AppSettings()
        self.mistral_service = MistralService(self.settings.mistral_api_key)
        self.qdrant_service = QdrantService(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key
        )
        
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "conversation_id" not in st.session_state:
            st.session_state.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def render_chat_interface(self):
        """Render the main chat interface."""
        st.title("🤖 AI Assistant")
        st.markdown("---")
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    if message["role"] == "assistant" and "context" in message:
                        # Show context sources if available
                        with st.expander("📚 Context Sources", expanded=False):
                            for i, source in enumerate(message["context"], 1):
                                st.write(f"**Source {i}:** {source.get('text', 'N/A')[:200]}...")
                    
                    st.markdown(format_message(message["content"]))
        
        # Chat input
        if prompt := st.chat_input("Ask me anything..."):
            self.handle_user_input(prompt)
    
    def handle_user_input(self, user_input: str):
        """Handle user input and generate response."""
        try:
            # Add user message to chat
            st.session_state.messages.append({
                "role": "user", 
                "content": user_input,
                "timestamp": datetime.now()
            })
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response_data = asyncio.run(self.generate_response(user_input))
                
                st.markdown(format_message(response_data["content"]))
                
                # Show context sources if available
                if response_data.get("context"):
                    with st.expander("📚 Context Sources", expanded=False):
                        for i, source in enumerate(response_data["context"], 1):
                            st.write(f"**Source {i}:** {source.get('text', 'N/A')[:200]}...")
            
            # Add assistant message to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_data["content"], 
                "context": response_data.get("context", []),
                "timestamp": datetime.now()
            })
            
        except Exception as e:
            logger.error(f"Error handling user input: {str(e)}")
            st.error("Sorry, I encountered an error. Please try again.")
    
    async def generate_response(self, user_input: str) -> Dict[str, Any]:
        """Generate response using Mistral API with Qdrant context."""
        try:
            # Get relevant context from Qdrant
            context_results = await self.qdrant_service.search_similar(
                query=user_input,
                limit=3
            )
            
            # Prepare context for Mistral
            context_text = "\n".join([
                result.get("text", "") for result in context_results
            ]) if context_results else ""
            
            # Generate response using Mistral
            response = await self.mistral_service.generate_response(
                user_input=user_input,
                context=context_text,
                conversation_history=st.session_state.messages[-5:]  # Last 5 messages
            )
            
            return {
                "content": response,
                "context": context_results
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "content": "I apologize, but I'm having trouble processing your request right now. Please try again.",
                "context": []
            }
    
    def render_sidebar(self):
        """Render the sidebar with controls and information."""
        with st.sidebar:
            st.header("⚙️ Controls")
            
            # Clear chat button
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
            
            # Export chat button
            if st.button("💾 Export Chat", use_container_width=True):
                self.export_chat()
            
            st.markdown("---")
            
            # Statistics
            st.header("📊 Session Stats")
            st.metric("Messages", len(st.session_state.messages))
            st.metric("Conversation ID", st.session_state.conversation_id)
            
            st.markdown("---")
            
            # About section
            st.header("ℹ️ About")
            st.markdown("""
            This AI assistant uses:
            - **Mistral AI** for natural language processing
            - **Qdrant** for semantic search and context retrieval
            - **Streamlit** for the user interface
            
            Built with ❤️ by Senior Python Engineers
            """)
    
    def export_chat(self):
        """Export chat history as JSON."""
        import json
        
        chat_data = {
            "conversation_id": st.session_state.conversation_id,
            "messages": [
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg["timestamp"].isoformat() if "timestamp" in msg else None
                }
                for msg in st.session_state.messages
            ]
        }
        
        st.download_button(
            label="Download Chat History",
            data=json.dumps(chat_data, indent=2),
            file_name=f"chat_export_{st.session_state.conversation_id}.json",
            mime="application/json"
        )
    
    def run(self):
        """Main application entry point."""
        try:
            # Configure page
            st.set_page_config(
                page_title="AI Assistant",
                page_icon="🤖",
                layout="wide",
                initial_sidebar_state="expanded"
            )
            
            # Apply custom CSS
            apply_custom_css()
            
            # Initialize session state
            self.initialize_session_state()
            
            # Render UI components
            self.render_sidebar()
            self.render_chat_interface()
            
        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            st.error("An error occurred while loading the application.")

def main():
    """Application entry point."""
    app = ChatbotApp()
    app.run()

if __name__ == "__main__":
    main()
