import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MistralService:
    """Service class for interacting with Mistral AI API."""
    
    def __init__(self, api_key: str, model: str = "mistral-medium"):
        """
        Initialize Mistral service.
        
        Args:
            api_key: Mistral API key
            model: Model name to use (default: mistral-medium)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_response(
        self, 
        user_input: str, 
        context: str = "", 
        conversation_history: List[Dict] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Generate a response using Mistral API.
        
        Args:
            user_input: User's message
            context: Additional context from vector database
            conversation_history: Previous conversation messages
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0.0-1.0)
            
        Returns:
            Generated response text
        """
        try:
            # Build messages for the conversation
            messages = self._build_messages(user_input, context, conversation_history)
            
            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 1,
                "random_seed": None,
                "safe_prompt": False,
                "stream": False
            }
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"].strip()
                    else:
                        error_text = await response.text()
                        logger.error(f"Mistral API error: {response.status} - {error_text}")
                        return "I apologize, but I'm experiencing technical difficulties. Please try again."
                        
        except asyncio.TimeoutError:
            logger.error("Mistral API request timed out")
            return "The request timed out. Please try again with a shorter message."
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I encountered an error while processing your request. Please try again."
    
    def _build_messages(
        self, 
        user_input: str, 
        context: str = "", 
        conversation_history: List[Dict] = None
    ) -> List[Dict[str, str]]:
        """
        Build the messages array for the Mistral API request.
        
        Args:
            user_input: Current user message
            context: Context from vector database
            conversation_history: Previous messages
            
        Returns:
            List of message dictionaries
        """
        messages = []
        
        # System message with context
        system_content = self._build_system_prompt(context)
        messages.append({
            "role": "system",
            "content": system_content
        })
        
        # Add conversation history (limited to prevent token overflow)
        if conversation_history:
            # Take last 5 messages to maintain context while staying within limits
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            
            for msg in recent_history:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        return messages
    
    def _build_system_prompt(self, context: str = "") -> str:
        """
        Build the system prompt with optional context.
        
        Args:
            context: Additional context from vector database
            
        Returns:
            System prompt string
        """
        base_prompt = """You are a helpful, knowledgeable AI assistant. You provide accurate, thoughtful, and engaging responses to user questions. You are friendly but professional, and you aim to be as helpful as possible.

Guidelines:
- Provide clear, well-structured responses
- If you're not sure about something, say so
- Use formatting (markdown) to make responses more readable
- Be conversational but informative
- If relevant context is provided, use it to enhance your responses"""

        if context.strip():
            context_prompt = f"""

RELEVANT CONTEXT:
The following context may be relevant to the user's question:
{context}

Use this context to inform your response when relevant, but don't mention that you're using provided context unless it's directly relevant to cite sources."""
            
            return base_prompt + context_prompt
        
        return base_prompt
    
    async def health_check(self) -> bool:
        """
        Check if the Mistral API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/models",
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Mistral API health check failed: {str(e)}")
            return False
    
    async def get_available_models(self) -> List[str]:
        """
        Get list of available models from Mistral API.
        
        Returns:
            List of model names
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/models",
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return [model["id"] for model in result.get("data", [])]
                    else:
                        logger.error(f"Failed to get models: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            return []
    
    def set_model(self, model: str):
        """
        Change the model used for generation.
        
        Args:
            model: New model name
        """
        self.model = model
        logger.info(f"Mistral model changed to: {model}")
    
    def get_current_model(self) -> str:
        """
        Get the currently used model.
        
        Returns:
            Current model name
        """
        return self.model