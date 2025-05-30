# API Documentation

## Overview

This document describes the internal API structure and service interfaces for the Mistral-Qdrant Chatbot application.

## Service Architecture

### Mistral Service (`Services/mistral_service.py`)

The Mistral service handles all interactions with the Mistral AI API for natural language processing and response generation.

#### Key Methods

```python
class MistralService:
    def __init__(self, api_key: str, model: str = "mistral-medium")
    def generate_response(self, messages: List[Dict], context: str = None) -> str
    def create_embedding(self, text: str) -> List[float]
    def stream_response(self, messages: List[Dict], context: str = None) -> Iterator[str]
```

#### Usage Example

```python
from Services.mistral_service import MistralService

mistral = MistralService(api_key="your-api-key")
response = mistral.generate_response([
    {"role": "user", "content": "Hello, how are you?"}
])
```

### Qdrant Service (`Services/qdrant_service.py`)

The Qdrant service manages vector database operations for semantic search and context retrieval.

#### Key Methods

```python
class QdrantService:
    def __init__(self, host: str, port: int, collection_name: str)
    def search_similar(self, query_vector: List[float], limit: int = 5) -> List[Dict]
    def add_document(self, text: str, metadata: Dict = None) -> str
    def delete_document(self, doc_id: str) -> bool
    def create_collection(self, vector_size: int = 1536) -> bool
```

#### Usage Example

```python
from Services.qdrant_service import QdrantService

qdrant = QdrantService(host="localhost", port=6333, collection_name="documents")
results = qdrant.search_similar(query_vector, limit=3)
```

## Component APIs

### Chat Widgets (`components/chat_widgets.py`)

Custom Streamlit components for enhanced chat experience.

#### Available Components

- `chat_message(message, is_user=False, avatar=None)`
- `typing_indicator()`
- `chat_input_with_history(key, placeholder="Type your message...")`
- `message_rating(message_id)`

### File Uploader (`components/file_uploader.py`)

Handles file upload and processing for document ingestion.

#### Methods

- `upload_and_process_file(accepted_types=['txt', 'pdf', 'docx'])`
- `process_document(file_content, file_type)`
- `chunk_text(text, chunk_size=500, overlap=50)`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MISTRAL_API_KEY` | Mistral AI API key | Required |
| `QDRANT_HOST` | Qdrant server host | `localhost` |
| `QDRANT_PORT` | Qdrant server port | `6333` |
| `COLLECTION_NAME` | Qdrant collection name | `chatbot_docs` |
| `MODEL_NAME` | Mistral model to use | `mistral-medium` |
| `MAX_TOKENS` | Maximum tokens per response | `1000` |
| `TEMPERATURE` | Model temperature | `0.7` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Settings Structure

```python
from Config.settings import Settings

settings = Settings()
print(settings.mistral_api_key)
print(settings.qdrant_config)
```

## Error Handling

All services implement consistent error handling:

```python
try:
    response = mistral_service.generate_response(messages)
except MistralAPIError as e:
    logger.error(f"Mistral API error: {e}")
    # Handle API-specific errors
except QdrantConnectionError as e:
    logger.error(f"Qdrant connection error: {e}")
    # Handle database connection errors
```

## Rate Limiting

The application implements rate limiting to prevent API abuse:

- Mistral API: 10 requests per minute per user
- Qdrant operations: 100 operations per minute per user

## Health Checks

Health check endpoints are available at:

- `/health` - Overall application health
- `/health/mistral` - Mistral API connectivity
- `/health/qdrant` - Qdrant database connectivity

## Logging

All services use structured logging with the following levels:

- `DEBUG`: Detailed diagnostic information
- `INFO`: General operational messages
- `WARNING`: Warning messages for recoverable errors
- `ERROR`: Error messages for failures
- `CRITICAL`: Critical errors that may cause shutdown

## Security Considerations

- API keys are stored securely using environment variables
- Input validation is performed on all user inputs
- Rate limiting prevents abuse
- CORS is configured for production deployment
- SSL/TLS encryption is recommended for production

## Testing

Run the test suite:

```bash
pytest tests/ -v --cov=Services --cov=components
```

## Performance Optimization

- Vector search results are cached for 5 minutes
- Mistral responses use streaming for better UX
- Database connection pooling is implemented
- Static assets are compressed and cached
