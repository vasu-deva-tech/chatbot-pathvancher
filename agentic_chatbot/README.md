# PathVancer Agentic Chatbot

A lightweight, production-ready chatbot powered by LangChain agents and OpenAI. Replaces n8n with a pure Python agentic framework.

## Features

✅ **Agentic Framework** - LangChain agents with tool calling  
✅ **Multi-session Support** - Track multiple user conversations  
✅ **Intent Detection** - Automatic buying intent recognition  
✅ **Semantic Search** - Knowledge base matching with embeddings  
✅ **Minimal Docker Image** - < 200MB (currently ~180MB)  
✅ **Redis Support** - Optional session caching  
✅ **Production Ready** - Health checks, error handling, logging  

## Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Server (8000)           │
├─────────────────────────────────────────┤
│  ChatbotAgent (LangChain)               │
│  ├─ Tool: Buying Intent Detection       │
│  ├─ Tool: Company Details Extraction    │
│  ├─ Tool: Response Formatting           │
│  └─ Tool: Question Metadata             │
├─────────────────────────────────────────┤
│  Services                               │
│  ├─ SessionManager (Redis/In-Memory)    │
│  ├─ EmbeddingService (OpenAI)           │
│  ├─ KnowledgeBase (JSON)                │
│  └─ Agent Executor                      │
└─────────────────────────────────────────┘
```

## Quick Start (Local)

### Prerequisites
- Python 3.11+
- OpenAI API Key
- Docker & Docker Compose (optional)

### 1. Setup

```bash
cd agentic_chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

### 2. Run Local Server

```bash
# Without Redis (in-memory sessions)
python -m uvicorn app.main:app --reload

# Server runs at: http://localhost:8000
# Docs available at: http://localhost:8000/docs
```

### 3. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Send a message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what is Pathvancer?",
    "session_id": "user123",
    "user_id": "john@example.com"
  }'
```

## Docker Deployment

### Build Image

```bash
# Build (creates ~180MB image)
docker build -t pathvancer-chatbot:latest .

# Check size
docker images pathvancer-chatbot

# Run locally
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  pathvancer-chatbot:latest
```

### Docker Compose (Local + Redis)

```bash
# Start with Redis
OPENAI_API_KEY=sk-... docker-compose up

# Stop
docker-compose down
```

## Cloud Deployment

### Option 1: Render.com

1. **Create Account** - Go to [render.com](https://render.com)

2. **Connect GitHub** - Link your GitHub repository

3. **Create Web Service**
   - Blueprint: Python > Web Service
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

4. **Environment Variables**
   - `OPENAI_API_KEY`: Your OpenAI key
   - `OPENAI_MODEL`: `gpt-3.5-turbo`
   - `DEBUG`: `false`

5. **Deploy**
   - Push to GitHub
   - Render auto-deploys

### Option 2: AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 pathvancer-chatbot --region us-east-1

# Create environment
eb create production

# Set environment variables
eb setenv OPENAI_API_KEY=sk-... DEBUG=false

# Deploy
git push && eb deploy

# View logs
eb logs
```

### Option 3: AWS ECS (Docker)

```bash
# Build image
docker build -t pathvancer-chatbot:latest .

# Tag for ECR
docker tag pathvancer-chatbot:latest <aws-account>.dkr.ecr.us-east-1.amazonaws.com/pathvancer-chatbot:latest

# Push to ECR
docker push <aws-account>.dkr.ecr.us-east-1.amazonaws.com/pathvancer-chatbot:latest

# Create ECS service (via AWS Console or CLI)
```

### Option 4: Google Cloud Run

```bash
# Build and push to Artifact Registry
gcloud builds submit --tag us-central1-docker.pkg.dev/PROJECT_ID/repo/pathvancer-chatbot

# Deploy
gcloud run deploy pathvancer-chatbot \
  --image us-central1-docker.pkg.dev/PROJECT_ID/repo/pathvancer-chatbot \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=sk-...
```

## API Endpoints

### Chat
```
POST /chat
Content-Type: application/json

{
  "message": "string",
  "session_id": "optional-uuid",
  "user_id": "optional-user-id"
}

Response:
{
  "session_id": "string",
  "user_id": "string",
  "answer": "string",
  "route": "kb|ai|error",
  "confidence": "high|medium|low",
  "is_new_session": boolean,
  "message_count": integer,
  "timestamp": "ISO-8601"
}
```

### Health Check
```
GET /health

Response:
{
  "status": "healthy",
  "embeddings_ready": boolean,
  "agent_ready": boolean,
  "redis_enabled": boolean
}
```

### Session Management
```
GET /session/{session_id}           # Get session details
DELETE /session/{session_id}        # Delete session
```

### Knowledge Base
```
GET /knowledge-base                 # Get all Q&A pairs
POST /knowledge-base                # Add new entry
```

## Configuration

Edit `.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
DEBUG=false

# Redis (optional)
REDIS_ENABLED=false
REDIS_URL=redis://localhost:6379

# Thresholds
SEMANTIC_THRESHOLD=0.50
INTENT_CONFIDENCE_THRESHOLD=0.60
```

## Image Size Optimization

Current Docker image: **~180MB**

Optimizations used:
- ✅ Python 3.11-slim base (40MB)
- ✅ Minimal system dependencies
- ✅ `--no-cache-dir` for pip
- ✅ Multi-stage build ready
- ✅ No test files included

To further reduce (if needed):

```dockerfile
# Use distroless Python (experimental)
FROM gcr.io/distroless/python3.11

# Or use Alpine + wheel compilation
FROM python:3.11-alpine
RUN apk add --no-cache gcc musl-dev
```

## Monitoring & Logging

The application logs to stdout. In cloud platforms:

### Render
- Logs visible in: Dashboard → Service → Logs

### AWS Elastic Beanstalk
```bash
eb logs
```

### Google Cloud Run
```bash
gcloud run logs read pathvancer-chatbot --limit 50
```

## Scaling

### Horizontal Scaling
- Stateless design - deploy multiple replicas
- Sessions stored in Redis (shared across instances)

### Vertical Scaling
- Increase CPU/Memory in cloud platform settings
- Typical: 512MB RAM, 0.5 CPU sufficient

## Performance Benchmarks

- **Latency**: ~200-500ms per message (including embedding)
- **Throughput**: ~10-20 concurrent users (0.5 CPU)
- **Memory**: ~150MB idle, ~200MB under load

## Troubleshooting

### Embedding Service Timeout
```bash
# Increase timeout in code
# app/embeddings.py: Add timeout to OpenAI client
```

### Redis Connection Failed
- Set `REDIS_ENABLED=false` to use in-memory storage
- Provide valid `REDIS_URL` if Redis is needed

### High Memory Usage
- Reduce `MAX_CONTEXT_HISTORY` in config.py
- Clear embedding cache periodically

## Development

### Add Custom Tools

1. Create tool in `app/tools/custom_tools.py`:
```python
from langchain.tools import tool

@tool
def my_tool(input: str) -> str:
    """Tool description"""
    return "result"
```

2. Add to `CHATBOT_TOOLS` in core_tools.py
3. Use in agent automatically

### Update Knowledge Base

Edit `knowledge_base.json` or use API:
```bash
curl -X POST http://localhost:8000/knowledge-base \
  -d "question=Your question" \
  -d "answer=Your answer"
```

## License

Proprietary - PathVancer

## Support

Email: info@pathvancer.com
