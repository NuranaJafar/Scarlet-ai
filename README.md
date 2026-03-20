# Scarlet Witch AI 🎃

A full-stack AI chat application with advanced memory management, emotion detection, and beautiful UI. Powered by OpenAI's GPT models.

## Features

- 🤖 **AI Chat Interface** - Powered by OpenAI's latest models
- 💾 **Persistent Memory** - Store and manage user memories across conversations
- 😊 **Emotion Detection** - Analyze sentiment and emotions in conversations
- 🎨 **Beautiful UI** - Modern, responsive design with light/dark themes
- 🔒 **Secure** - JWT authentication and secure password handling
- 📱 **Mobile Friendly** - Works seamlessly on desktop and mobile
- 🐳 **Docker Ready** - Easy deployment with Docker and Docker Compose

## Project Structure

```
scarlet-witch-ai/
├── backend/              # Python Flask API
│   ├── app/
│   │   ├── models.py    # Database models
│   │   ├── routes.py    # API endpoints
│   │   ├── config.py    # Configuration
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   ├── requirements.txt
│   └── run.py
├── frontend/            # Web UI
│   ├── index.html
│   ├── css/
│   └── js/
├── database/            # Database initialization
│   └── init.sql
├── docker-compose.yml
├── Dockerfile
└── .env
```

## Prerequisites

- Python 3.11+
- Node.js 16+ (optional, for development)
- Docker & Docker Compose (for containerized deployment)
- OpenAI API Key

## Installation

### Option 1: Local Development

1. Clone the repository
```bash
git clone https://github.com/yourusername/scarlet-witch-ai.git
cd scarlet-witch-ai
```

2. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

4. Run the backend
```bash
python run.py
```

5. Serve the frontend
```bash
# Using Python
python -m http.server 8000 --directory frontend

# Or using any HTTP server
npx http-server frontend
```

6. Open http://localhost:8000 in your browser

### Option 2: Docker Compose

1. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. Start the application
```bash
docker-compose up -d
```

3. Open http://localhost in your browser

## API Documentation

### Authentication
All API endpoints (except `/health`) require a JWT token in the `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

### Endpoints

#### Health Check
```
GET /api/health
```

#### Chat
```
POST /api/chat
Content-Type: application/json

{
  "message": "Hello, how are you?",
  "conversation_id": 1,
  "store_memory": false
}
```

#### Memory Management
```
GET /api/memory - Get all memories
POST /api/memory - Store a memory
PUT /api/memory - Update a memory
DELETE /api/memory - Delete a memory
```

#### Conversations
```
GET /api/conversations - Get user's conversations
```

## Configuration

Key environment variables:

- `FLASK_ENV` - Development or production
- `DATABASE_URL` - Database connection string
- `OPENAI_API_KEY` - OpenAI API key
- `MODEL_NAME` - AI model to use (default: gpt-3.5-turbo)
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key

## Development

### Running Tests
```bash
cd backend
python -m pytest
```

### Code Style
```bash
# Format code
black backend/

# Lint code
flake8 backend/
```

## Deployment

### Using Docker Compose
```bash
docker-compose -f docker-compose.yml up -d
```

### Using Kubernetes
Create appropriate manifests and deploy using:
```bash
kubectl apply -f k8s/
```

## Features in Detail

### Emotion Detection
The application analyzes user messages to detect emotions (happy, sad, angry, confused, anxious, neutral).

### Memory Management
Users can store important information that the AI remembers across conversations.

### Conversation History
All conversations are saved and can be accessed later.

## Security

- Passwords are hashed using secure algorithms
- JWT tokens for stateless authentication
- CORS protection
- SQL injection prevention
- XSS protection headers
- Rate limiting on API endpoints

## Performance

- Gzip compression for assets
- Efficient caching strategies
- Database indexing
- Connection pooling
- Request throttling

## Troubleshooting

### API Connection Issues
- Verify the backend is running on port 5000
- Check CORS settings in config
- Ensure firewall allows connections

### Memory Not Saving
- Check database is accessible
- Verify user is authenticated
- Check API response for errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues and questions, please open an GitHub issue or contact support.

## Changelog

### v1.0.0 (2024-03-20)
- Initial release
- Core chat functionality
- Memory management
- Emotion detection
- Docker support

---

Made with ❤️ and AI
