AI Chatbot with Semantic Search
A sophisticated chatbot application built with Streamlit, Mistral AI, and Qdrant vector database for semantic search and context-aware responses.

🚀 Features
Interactive Chat Interface: Beautiful Streamlit-based UI with custom styling
Semantic Search: Qdrant vector database integration for context retrieval
AI-Powered Responses: Mistral API integration for natural language processing
Document Upload: Support for multiple file formats (PDF, TXT, DOCX, MD)
Dockerized Deployment: Complete containerization with Docker Compose
Production Ready: Nginx reverse proxy, Supervisor process management
Health Monitoring: Built-in health checks and logging
Extensible Architecture: Modular design with clean separation of concerns
📋 Prerequisites
Docker and Docker Compose
Python 3.9+ (for local development)
Mistral API key
Qdrant instance (or use Docker Compose setup)
🛠️ Quick Start
1. Clone and Setup
bash
git clone <repository-url>
cd ai-chatbot
cp .env.example .env
# Edit .env with your API keys and configuration
2. Docker Compose Deployment (Recommended)
bash
# Start all services
docker-compose up -d

# Initialize database
docker-compose exec app python scripts/setup_database.py

# Load sample data
docker-compose exec app python data_loader.py --path ./data/sample_docs/
3. Local Development
bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Qdrant (using Docker)
docker run -p 6333:6333 qdrant/qdrant

# Run the application
streamlit run app.py
🏗️ Architecture
├── app.py                          # Main Streamlit application
├── services/                       # Core business logic
│   ├── mistral_service.py         # Mistral API integration
│   └── qdrant_service.py          # Vector database operations
├── components/                     # Reusable UI components
│   ├── chat_widgets.py           # Custom chat components
│   └── file_uploader.py          # File upload functionality
├── utils/                         # Utility functions
│   ├── ui_helpers.py             # UI helper functions
│   ├── logger.py                 # Logging configuration
│   └── text_processing.py        # Text preprocessing
├── config/                        # Configuration
│   └── settings.py               # Application settings
├── scripts/                       # Database and maintenance scripts
│   ├── setup_database.py         # Database initialization
│   └── health_check.py           # Health monitoring
├── static/                        # Static assets
│   ├── css/                      # Custom styling
│   ├── js/                       # JavaScript enhancements
│   └── images/                   # Image assets
├── tests/                         # Test suite
├── docs/                          # Documentation
└── deployment/                    # Production deployment configs
    ├── nginx.conf                # Nginx configuration
    └── supervisor.conf           # Process management
⚡ Configuration
Environment Variables
Key configuration options in .env:

env
# API Configuration
MISTRAL_API_KEY=your_api_key
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Application Settings
APP_TITLE=AI Chatbot Assistant
DEBUG=False
LOG_LEVEL=INFO

# UI Customization
THEME=dark
CHAT_HISTORY_LIMIT=50
Qdrant Setup
The application automatically creates collections with optimal settings:

Vector Size: 1024 dimensions (Mistral embeddings)
Distance Metric: Cosine similarity
Indexing: HNSW for fast approximate search
🎨 UI Customization
Custom Styling
The application includes custom CSS for enhanced visual appeal:

Dark/Light theme support
Glassmorphism effects
Smooth animations
Responsive design
Custom chat bubbles
Themes
Switch between themes by updating the THEME environment variable:

dark - Modern dark theme with blue accents
light - Clean light theme
custom - Load custom CSS from static/css/custom.css
📊 Usage Examples
Basic Chat
python
# Simple question-answer
user: "What is machine learning?"
bot: [Retrieves relevant context from documents and provides comprehensive answer]
Document-Based Queries
python
# Upload documents first, then ask specific questions
user: "Based on the uploaded documents, what are the key findings about AI ethics?"
bot: [Searches document vectors and provides contextual response]
File Upload
Drag and drop files in the sidebar
Supported formats: PDF, TXT, DOCX, MD
Automatic text extraction and vectorization
Real-time indexing to Qdrant
🔧 Development
Running Tests
bash
# Run all tests
pytest

# Run with coverage
pytest --cov=services --cov=utils --cov-report=html

# Run specific test categories
pytest tests/test_services.py -v
Adding New Features
New Services: Add to services/ directory
UI Components: Create in components/
Utilities: Add to utils/
Tests: Mirror structure in tests/
Code Style
The project follows PEP 8 standards with additional conventions:

Type hints for all functions
Comprehensive docstrings
Error handling with custom exceptions
Logging for debugging and monitoring
🚀 Production Deployment
Using Docker Compose
bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Scale the application
docker-compose -f docker-compose.prod.yml up -d --scale app=3
Manual Deployment
Setup Nginx: Use provided nginx.conf
Configure Supervisor: Use supervisor.conf for process management
Environment: Set ENVIRONMENT=production in .env
SSL: Configure SSL certificates for HTTPS
Monitoring: Setup health check endpoints
Health Monitoring
bash
# Check application health
curl http://localhost:8501/health

# Database connectivity
python scripts/health_check.py

# View logs
docker-compose logs -f app
🔍 Troubleshooting
Common Issues
Mistral API Errors
Check API key validity
Verify rate limits
Monitor API quotas
Qdrant Connection Issues
Ensure Qdrant is running
Check network connectivity
Verify collection exists
File Upload Problems
Check file size limits
Verify supported formats
Review upload directory permissions
Debug Mode
Enable debug mode for detailed logging:

bash
export DEBUG=True
export LOG_LEVEL=DEBUG
streamlit run app.py
📈 Performance Optimization
Vector Search Optimization
Use appropriate vector dimensions
Optimize HNSW parameters
Implement result caching
Batch operations for bulk uploads
Application Performance
Enable Streamlit caching
Optimize database queries
Use connection pooling
Implement response streaming
🤝 Contributing
Fork the repository
Create a feature branch
Make your changes
Add tests for new functionality
Ensure all tests pass
Submit a pull request
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🆘 Support
For support and questions:

Create an issue in the GitHub repository
Check the documentation in the docs/ directory
Review the troubleshooting section above
🔮 Roadmap
 Multi-language support
 Advanced analytics dashboard
 Integration with more LLM providers
 Real-time collaboration features
 Mobile-responsive improvements
 Voice input/output capabilities
