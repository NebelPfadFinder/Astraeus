# User Guide

## Getting Started

Welcome to the Mistral-Qdrant Chatbot! This guide will help you understand how to use the application effectively.

## Features Overview

### 1. Interactive Chat Interface
- Clean, modern chat interface built with Streamlit
- Real-time message streaming
- Message history and conversation context
- User avatar and typing indicators

### 2. Document Upload and Processing
- Upload documents in various formats (PDF, DOCX, TXT)
- Automatic text extraction and chunking
- Vector embedding generation and storage
- Searchable document knowledge base

### 3. Semantic Search Integration
- Context-aware responses using document knowledge
- Relevant information retrieval from uploaded documents
- Citation and source referencing in responses

### 4. Customizable Chat Experience
- Message rating and feedback system
- Export conversation history
- Multiple conversation threads
- Custom themes and styling

## Using the Chat Interface

### Starting a Conversation

1. **Access the Application**
   - Open your web browser and navigate to the application URL
   - The chat interface will load automatically

2. **Send Your First Message**
   - Type your message in the input box at the bottom
   - Press Enter or click the Send button
   - The chatbot will respond using Mistral AI

3. **Context-Aware Conversations**
   - The chatbot maintains conversation history
   - Responses consider previous messages for context
   - Use follow-up questions naturally

### Example Conversations

```
User: What is machine learning?
Bot: Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed...

User: Can you give me an example?
Bot: Based on our previous discussion about machine learning, here's a practical example: email spam detection...
```

## Document Management

### Uploading Documents

1. **Access File Upload**
   - Click on the "Upload Documents" section in the sidebar
   - Or use the file upload widget in the main interface

2. **Supported File Types**
   - PDF documents (.pdf)
   - Microsoft Word documents (.docx, .doc)
   - Plain text files (.txt)
   - Markdown files (.md)

3. **Upload Process**
   - Select your file(s) using the file picker
   - Wait for processing confirmation
   - Documents are automatically indexed for search

### Using Document Context

Once documents are uploaded, the chatbot can reference them in responses:

```
User: What does the quarterly report say about sales?
Bot: Based on the quarterly report you uploaded, sales increased by 15% compared to the previous quarter...
```

## Advanced Features

### Message Rating System

Help improve the chatbot by rating responses:

1. Click the thumbs up/down icons after each response
2. Provide optional feedback in the text box
3. Ratings help improve future responses

### Conversation Export

Export your chat history:

1. Click "Export Conversation" in the sidebar
2. Choose format (JSON, TXT, or PDF)
3. Download the exported file

### Multiple Conversations

Manage multiple conversation threads:

1. Click "New Conversation" to start fresh
2. Switch between conversations using the sidebar
3. Each conversation maintains its own context

## Keyboard Shortcuts

- **Enter**: Send message
- **Shift + Enter**: New line in message
- **Ctrl + K**: Focus on search/input
- **Ctrl + N**: New conversation
- **Ctrl + E**: Export conversation

## Troubleshooting

### Common Issues

**1. Slow Responses**
- Check your internet connection
- Large documents may take time to process
- Server may be under high load

**2. Upload Failures**
- Ensure file size is under 10MB
- Check file format is supported
- Try refreshing the page and uploading again

**3. Connection Errors**
- Refresh the page
- Check if the service is available
- Contact administrator if issues persist

### Getting Help

**Error Messages**
- Error messages appear in red at the top of the chat
- Include error details when reporting issues

**Contact Support**
- Use the feedback form in the application
- Email: support@yourorganization.com
- Include your conversation ID for faster assistance

## Best Practices

### Effective Prompting

1. **Be Specific**
   ```
   Good: "Explain the benefits of renewable energy for businesses"
   Poor: "Tell me about energy"
   ```

2. **Provide Context**
   ```
   Good: "Based on the climate report I uploaded, what are the key findings about temperature changes?"
   Poor: "What does the report say?"
   ```

3. **Ask Follow-up Questions**
   - Build on previous responses
   - Ask for clarification when needed
   - Request examples or elaboration

### Document Organization

1. **Use Descriptive Filenames**
   - Instead of "document1.pdf", use "quarterly_sales_report_q3_2024.pdf"

2. **Upload Related Documents Together**
   - Group related documents for better context
   - Upload reference materials before asking questions

3. **Keep Documents Updated**
   - Remove outdated documents
   - Upload new versions when available

## Privacy and Security

### Data Handling
- Conversations are stored securely
- Documents are processed and vectorized locally
- No data is shared with third parties without consent

### Privacy Controls
- Clear conversation history anytime
- Delete uploaded documents
- Export your data before deletion

### Security Features
- Encrypted connections (HTTPS)
- Secure API key management
- Regular security updates

## Customization Options

### Theme Settings
- Light/Dark mode toggle
- Custom color schemes
- Font size adjustment

### Interface Preferences
- Message display density
- Sidebar layout options
- Chat bubble styling

### Notification Settings
- Response completion alerts
- Error notifications
- System status updates

## API Integration

For developers wanting to integrate with the chatbot:

### REST API Endpoints
- `POST /api/chat` - Send chat message
- `GET /api/conversations` - List conversations
- `POST /api/upload` - Upload document
- `GET /api/health` - System status

### WebSocket Support
- Real-time message streaming
- Live typing indicators
- Connection status updates

## Feedback and Improvement

Your feedback helps improve the chatbot:

1. **Rate Responses** - Use thumbs up/down buttons
2. **Report Issues** - Use the feedback form
3. **Suggest Features** - Contact support with ideas
4. **Share Use Cases** - Help us understand your needs

## Updates and Maintenance

### Automatic Updates
- Security patches applied automatically
- Feature updates deployed regularly
- Notification of major changes

### Maintenance Windows
- Scheduled maintenance announcements
- Minimal downtime during updates
- Backup and recovery procedures

Thank you for using the Mistral-Qdrant Chatbot! For additional support, please refer to the FAQ section or contact our support team.
