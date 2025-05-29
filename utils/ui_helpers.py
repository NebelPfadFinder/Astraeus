# enhanced_ui_components.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any
import asyncio
import time

class EnhancedChatUI:
    """Enhanced UI components for the chatbot interface."""
    
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="AI Assistant Pro",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/your-repo',
                'Report a bug': 'https://github.com/your-repo/issues',
                'About': "AI Assistant powered by Mistral AI and Qdrant"
            }
        )
    
    def initialize_session_state(self):
        """Initialize enhanced session state variables."""
        if "enhanced_mode" not in st.session_state:
            st.session_state.enhanced_mode = True
        if "theme" not in st.session_state:
            st.session_state.theme = "default"
        if "chat_stats" not in st.session_state:
            st.session_state.chat_stats = {
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "session_start": datetime.now(),
                "response_times": []
            }
        if "conversation_memory" not in st.session_state:
            st.session_state.conversation_memory = []
    
    def render_header(self):
        """Render enhanced header with branding and status."""
        header_col1, header_col2, header_col3 = st.columns([2, 3, 2])
        
        with header_col1:
            st.image("https://via.placeholder.com/100x40/667eea/ffffff?text=AI", width=100)
        
        with header_col2:
            st.markdown("""
            <div style="text-align: center;">
                <h1 style="margin: 0; background: linear-gradient(45deg, #667eea, #764ba2); 
                           -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    🤖 AI Assistant Pro
                </h1>
                <p style="color: #666; margin: 0;">Powered by Mistral AI & Qdrant</p>
            </div>
            """, unsafe_allow_html=True)
        
        with header_col3:
            self.render_status_indicators()
    
    def render_status_indicators(self):
        """Render system status indicators."""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.get("mistral_status", True):
                st.success("🟢 Mistral AI", icon="✅")
            else:
                st.error("🔴 Mistral AI", icon="❌")
        
        with col2:
            if st.session_state.get("qdrant_status", True):
                st.success("🟢 Qdrant DB", icon="✅")
            else:
                st.error("🔴 Qdrant DB", icon="❌")
    
    def render_chat_interface(self):
        """Render enhanced chat interface with animations."""
        # Create chat container with custom styling
        chat_container = st.container()
        
        with chat_container:
            # Custom CSS for chat animations
            st.markdown("""
            <style>
            .chat-message {
                animation: fadeInUp 0.5s ease-out;
                margin-bottom: 1rem;
            }
            
            .user-message {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 20px 20px 5px 20px;
                padding: 12px 16px;
                margin-left: 20%;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            
            .assistant-message {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid #e1e8ed;
                border-radius: 20px 20px 20px 5px;
                padding: 12px 16px;
                margin-right: 20%;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .typing-indicator {
                display: flex;
                align-items: center;
                padding: 12px 16px;
                background: rgba(102, 126, 234, 0.1);
                border-radius: 20px;
                margin-right: 20%;
                margin-bottom: 1rem;
            }
            
            .typing-dots {
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
            """, unsafe_allow_html=True)
            
            # Display conversation history
            for i, message in enumerate(st.session_state.messages):
                self.render_message(message, i)
    
    def render_message(self, message: Dict, index: int):
        """Render individual message with enhanced styling."""
        timestamp = message.get("timestamp", datetime.now()).strftime("%H:%M")
        
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message">
                <div class="user-message">
                    <strong>You</strong> • <small>{timestamp}</small><br>
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        elif message["role"] == "assistant":
            col1, col2 = st.columns([1, 10])
            
            with col1:
                st.markdown("🤖", help="AI Assistant")
            
            with col2:
                st.markdown(f"""
                <div class="chat-message">
                    <div class="assistant-message">
                        <strong>AI Assistant</strong> • <small>{timestamp}</small><br>
                        {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show context sources if available
                if message.get("context"):
                    with st.expander("📚 Sources Used", expanded=False):
                        for i, source in enumerate(message["context"], 1):
                            st.markdown(f"""
                            **Source {i}** (Score: {source.get('score', 0):.3f})
                            ```
                            {source.get('text', 'N/A')[:200]}...
                            ```
                            """)
    
    def render_typing_indicator(self):
        """Show typing indicator during response generation."""
        typing_placeholder = st.empty()
        typing_placeholder.markdown("""
        <div class="typing-indicator">
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            <span style="margin-left: 10px; color: #666;">AI is thinking...</span>
        </div>
        """, unsafe_allow_html=True)
        return typing_placeholder
    
    def render_advanced_sidebar(self):
        """Render enhanced sidebar with analytics and controls."""
        with st.sidebar:
            # Logo and branding
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h2>🤖 Control Panel</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Quick Actions
            self.render_quick_actions()
            
            st.divider()
            
            # Chat Analytics
            self.render_chat_analytics()
            
            st.divider()
            
            # Settings
            self.render_settings_panel()
            
            st.divider()
            
            # System Info
            self.render_system_info()
    
    def render_quick_actions(self):
        """Render quick action buttons."""
        st.subheader("⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.chat_stats = {
                    "total_messages": 0,
                    "user_messages": 0,
                    "assistant_messages": 0,
                    "session_start": datetime.now(),
                    "response_times": []
                }
                st.rerun()
        
        with col2:
            if st.button("💾 Export", use_container_width=True):
                self.export_conversation()
        
        # Additional quick actions
        if st.button("🔄 New Session", use_container_width=True):
            self.start_new_session()
        
        if st.button("📊 Analytics", use_container_width=True):
            self.show_detailed_analytics()
    
    def render_chat_analytics(self):
        """Render real-time chat analytics."""
        st.subheader("📊 Session Analytics")
        
        stats = st.session_state.chat_stats
        session_duration = datetime.now() - stats["session_start"]
        
        # Metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Messages",
                value=stats["total_messages"],
                delta=f"+{len(st.session_state.messages) - stats.get('last_count', 0)}"
            )
        
        with col2:
            st.metric(
                label="Duration",
                value=f"{session_duration.seconds // 60}m",
                delta=f"{session_duration.seconds % 60}s"
            )
        
        # Response time chart
        if stats["response_times"]:
            avg_response = sum(stats["response_times"]) / len(stats["response_times"])
            st.metric(
                label="Avg Response",
                value=f"{avg_response:.1f}s",
                delta=f"±{max(stats['response_times']) - min(stats['response_times']):.1f}s"
            )
            
            # Mini chart
            fig = go.Figure(data=go.Scatter(
                y=stats["response_times"][-10:],  # Last 10 responses
                mode='lines+markers',
                line=dict(color='#667eea', width=2),
                marker=dict(size=6)
            ))
            fig.update_layout(
                height=150,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False,
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def render_settings_panel(self):
        """Render settings and preferences panel."""
        st.subheader("⚙️ Settings")
        
        # Theme selection
        theme = st.selectbox(
            "Theme",
            ["Default", "Dark", "Light", "Colorful"],
            index=0
        )
        st.session_state.theme = theme.lower()
        
        # Model settings
        with st.expander("🔧 Model Settings"):
            temperature = st.slider(
                "Creativity (Temperature)",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Higher values make responses more creative"
            )
            
            max_tokens = st.slider(
                "Response Length",
                min_value=100,
                max_value=2000,
                value=1000,
                step=100
            )
            
            st.session_state.model_settings = {
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        
        # Context settings
        with st.expander("🔍 Context Settings"):
            context_limit = st.slider(
                "Context Sources",
                min_value=1,
                max_value=10,
                value=3,
                help="Number of relevant sources to include"
            )
            
            score_threshold = st.slider(
                "Relevance Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.05,
                help="Minimum relevance score for context"
            )
            
            st.session_state.context_settings = {
                "limit": context_limit,
                "score_threshold": score_threshold
            }
    
    def render_system_info(self):
        """Render system information and health status."""
        st.subheader("ℹ️ System Info")
        
        # Health status
        health_status = self.check_system_health()
        
        if health_status["overall"]:
            st.success("✅ All Systems Operational")
        else:
            st.warning("⚠️ Some Issues Detected")
        
        # Detailed status
        with st.expander("🔍 Detailed Status"):
            st.write("**Services:**")
            st.write(f"• Mistral API: {'✅ Online' if health_status['mistral'] else '❌ Offline'}")
            st.write(f"• Qdrant DB: {'✅ Online' if health_status['qdrant'] else '❌ Offline'}")
            st.write(f"• Vector Store: {'✅ Ready' if health_status['vectors'] else '❌ Not Ready'}")
            
            st.write("**Performance:**")
            st.write(f"• Memory Usage: {health_status.get('memory', 'Unknown')}")
            st.write(f"• Response Time: {health_status.get('latency', 'Unknown')}")
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check system health status."""
        # This would integrate with your actual health check methods
        return {
            "overall": True,
            "mistral": True,
            "qdrant": True,
            "vectors": True,
            "memory": "45%",
            "latency": "250ms"
        }
    
    def export_conversation(self):
        """Export conversation with enhanced formatting."""
        import json
        from io import StringIO
        
        # Prepare export data
        export_data = {
            "conversation_id": st.session_state.conversation_id,
            "export_timestamp": datetime.now().isoformat(),
            "session_stats": st.session_state.chat_stats,
            "messages": [
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg.get("timestamp", datetime.now()).isoformat(),
                    "context_sources": len(msg.get("context", []))
                }
                for msg in st.session_state.messages
            ],
            "settings": {
                "model_settings": st.session_state.get("model_settings", {}),
                "context_settings": st.session_state.get("context_settings", {})
            }
        }
        
        # Create download button
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Download Conversation",
            data=json_str,
            file_name=f"chat_export_{st.session_state.conversation_id}.json",
            mime="application/json",
            use_container_width=True
        )
        
        st.success("✅ Conversation exported successfully!")
    
    def start_new_session(self):
        """Start a new conversation session."""
        st.session_state.messages = []
        st.session_state.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state.chat_stats = {
            "total_messages": 0,
            "user_messages": 0,
            "assistant_messages": 0,
            "session_start": datetime.now(),
            "response_times": []
        }
        st.success("🆕 New session started!")
        st.rerun()
    
    def show_detailed_analytics(self):
        """Show detailed analytics in a modal."""
        st.markdown("### 📈 Detailed Analytics")
        
        if not st.session_state.messages:
            st.info("No conversation data available yet.")
            return
        
        # Create analytics dashboard
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "⏱️ Timeline", "🎯 Performance"])
        
        with tab1:
            self.render_overview_analytics()
        
        with tab2:
            self.render_timeline_analytics()
        
        with tab3:
            self.render_performance_analytics()
    
    def render_overview_analytics(self):
        """Render overview analytics."""
        stats = st.session_state.chat_stats
        messages = st.session_state.messages
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Messages", len(messages))
        
        with col2:
            user_msgs = len([m for m in messages if m["role"] == "user"])
            st.metric("User Messages", user_msgs)
        
        with col3:
            ai_msgs = len([m for m in messages if m["role"] == "assistant"])
            st.metric("AI Responses", ai_msgs)
        
        with col4:
            if stats["response_times"]:
                avg_time = sum(stats["response_times"]) / len(stats["response_times"])
                st.metric("Avg Response Time", f"{avg_time:.1f}s")
            else:
                st.metric("Avg Response Time", "N/A")
        
        # Message length analysis
        if messages:
            msg_lengths = [len(m["content"]) for m in messages]
            
            fig = px.histogram(
                x=msg_lengths,
                title="Message Length Distribution",
                labels={"x": "Characters", "y": "Count"}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    def render_timeline_analytics(self):
        """Render timeline analytics."""
        messages = st.session_state.messages
        
        if not messages:
            st.info("No timeline data available.")
            return
        
        # Create timeline data
        timeline_data = []
        for i, msg in enumerate(messages):
            timestamp = msg.get("timestamp", datetime.now())
            timeline_data.append({
                "message_id": i,
                "timestamp": timestamp,
                "role": msg["role"],
                "length": len(msg["content"]),
                "has_context": len(msg.get("context", [])) > 0
            })
        
        df = pd.DataFrame(timeline_data)
        
        # Timeline chart
        fig = px.scatter(
            df,
            x="timestamp",
            y="length",
            color="role",
            size="length",
            title="Conversation Timeline",
            labels={"length": "Message Length", "timestamp": "Time"}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    def render_performance_analytics(self):
        """Render performance analytics."""
        stats = st.session_state.chat_stats
        
        if not stats["response_times"]:
            st.info("No performance data available yet.")
            return
        
        # Response time chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=stats["response_times"],
            mode='lines+markers',
            name='Response Time',
            line=dict(color='#667eea', width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Response Time Trend",
            yaxis_title="Time (seconds)",
            xaxis_title="Response Number",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Fastest Response", f"{min(stats['response_times']):.1f}s")
        
        with col2:
            st.metric("Slowest Response", f"{max(stats['response_times']):.1f}s")
        
        with col3:
            avg_time = sum(stats["response_times"]) / len(stats["response_times"])
            st.metric("Average Response", f"{avg_time:.1f}s")
    
    def apply_theme_styling(self):
        """Apply theme-specific styling."""
        theme_styles = {
            "dark": """
            <style>
            .stApp {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                color: #ffffff;
            }
            .chat-message { color: #ffffff; }
            </style>
            """,
            "light": """
            <style>
            .stApp {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                color: #212529;
            }
            </style>
            """,
            "colorful": """
            <style>
            .stApp {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
            }
            </style>
            """
        }
        
        current_theme = st.session_state.get("theme", "default")
        if current_theme in theme_styles:
            st.markdown(theme_styles[current_theme], unsafe_allow_html=True)
