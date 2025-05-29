import os
from typing import Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class AppSettings:
    """Application configuration settings."""
    
    # Mistral API Configuration
    mistral_api_key: str
    mistral_model: str = "mistral-medium"
    
    # Qdrant Configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "chatbot_knowledge"
    
    # Embedding Model Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # Chat Configuration
    max_tokens: int = 1000
    temperature: float = 0.7
    max_context_length: int = 4000
    
    # UI Configuration
    page_title: str = "AI Assistant"
    page_icon: str = "🤖"
    
    # Logging Configuration
    log_level: str = "INFO"
    
    def __init__(self):
        """Initialize settings from environment variables."""
        self.load_from_env()
        self.validate_settings()
    
    def load_from_env(self):
        """Load configuration from environment variables."""
        # Mistral Configuration
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY", "")
        self.mistral_model = os.getenv("MISTRAL_MODEL", "mistral-medium")
        
        # Qdrant Configuration
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.qdrant_collection_name = os.getenv("QDRANT_COLLECTION_NAME", "chatbot_knowledge")
        
        # Embedding Configuration
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.embedding_dimension = int(os.getenv("EMBEDDING_DIMENSION", "384"))
        
        # Chat Configuration
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.max_context_length = int(os.getenv("MAX_CONTEXT_LENGTH", "4000"))
        
        # UI Configuration
        self.page_title = os.getenv("PAGE_TITLE", "AI Assistant")
        self.page_icon = os.getenv("PAGE_ICON", "🤖")
        
        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
    
    def validate_settings(self):
        """Validate critical settings."""
        if not self.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is required")
        
        if self.temperature < 0 or self.temperature > 1:
            logger.warning("Temperature should be between 0 and 1, adjusting to valid range")
            self.temperature = max(0, min(1, self.temperature))
        
        if self.max_tokens < 1:
            logger.warning("max_tokens should be positive, setting to default")
            self.max_tokens = 1000
        
        logger.info("Settings validated successfully")
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return {
            "mistral_api_key": "***" if self.mistral_api_key else None,
            "mistral_model": self.mistral_model,
            "qdrant_url": self.qdrant_url,
            "qdrant_api_key": "***" if self.qdrant_api_key else None,
            "qdrant_collection_name": self.qdrant_collection_name,
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "max_context_length": self.max_context_length,
            "page_title": self.page_title,
            "page_icon": self.page_icon,
            "log_level": self.log_level
        }
    
    def get_mistral_config(self) -> dict:
        """Get Mistral-specific configuration."""
        return {
            "api_key": self.mistral_api_key,
            "model": self.mistral_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
    
    def get_qdrant_config(self) -> dict:
        """Get Qdrant-specific configuration."""
        return {
            "url": self.qdrant_url,
            "api_key": self.qdrant_api_key,
            "collection_name": self.qdrant_collection_name,
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension
        }
