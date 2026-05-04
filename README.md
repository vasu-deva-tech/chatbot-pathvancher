# Pathvancer Agentic Chatbot

Lightweight, multi-session chatbot powered by LangChain agents, OpenRouter AI, and Supabase.

## Features

- 🤖 **LangChain Agents** - Intelligent multi-tool agent orchestration
- 🔄 **Multi-Session Support** - Persistent conversation history with Supabase
- 🧠 **Semantic Search** - Knowledge base matching with embeddings
- 🚀 **OpenRouter API** - Cost-effective LLM access (supports 200+ models)
- 📦 **Docker Ready** - ~180MB optimized image
- ☁️ **Cloud Deployment** - Render, AWS, GCP, Docker Compose

## Quick Start

### Local Development

```bash
# Clone repository
git clone <your-repo-url>
cd pathvancer-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
cp .env.example .env
# Edit .env with your keys

# Run application
uvicorn app.main:app --reload
```

Application runs at `http://localhost:8000`

## Deployment on Render

### Prerequisites

1. **GitHub Repository**: Push code to GitHub (public or private)
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Supabase Project**: Create at [supabase.com](https://supabase.com)
4. **OpenRouter Account**: Sign up at [openrouter.io](https://openrouter.io)

### Setup Steps

#### 1. Create Supabase Tables

In your Supabase SQL editor, run:

```sql
-- Sessions table
CREATE TABLE sessions (
  session_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  last_activity TIMESTAMP DEFAULT NOW(),
  conversation_history TEXT DEFAULT '[]',
  context_data TEXT DEFAULT '{}',
  message_count INT DEFAULT 0,
  extracted_details TEXT DEFAULT '{}'
);

-- Messages table
CREATE TABLE messages (
  id BIGSERIAL PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES sessions(session_id),
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_messages_session_id ON messages(session_id);
```

#### 2. Get Your Credentials

- **SUPABASE_URL**: From Supabase project settings (Settings → API)
- **SUPABASE_KEY**: `service_role` key from Supabase API settings
- **OPENROUTER_API_KEY**: From OpenRouter dashboard

#### 3. Connect GitHub to Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub account
4. Select this repository
5. Configure:
   - **Name**: `pathvancer-chatbot`
   - **Environment**: `Python 3.11`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 4. Set Environment Variables

In Render dashboard, add these environment variables:

```
OPENROUTER_API_KEY=sk-or-v1-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
OPENROUTER_BASE_URL=https://openrouter.io/api/v1
LLM_MODEL=openai/gpt-3.5-turbo
EMBEDDING_MODEL=openai/text-embedding-3-small
SESSION_TIMEOUT=3600
MAX_CONTEXT_HISTORY=10
ENVIRONMENT=production
LOG_LEVEL=INFO
```

#### 5. Deploy

Click "Create Web Service" - Render will automatically build and deploy.

## API Endpoints

### Chat
```bash
POST /chat
Content-Type: application/json

{
  "message": "What are your products?",
  "session_id": "user-123-session",
  "user_id": "user-123"
}
```

### Health Check
```bash
GET /health
```

### Session Management
```bash
GET /session/{session_id}
DELETE /session/{session_id}
```

### Knowledge Base
```bash
GET /knowledge-base/search?query=products&top_k=5
POST /knowledge-base/add
Content-Type: application/json

{
  "question": "What is your product?",
  "answer": "We offer..."
}
```

## Environment Variables

| Variable | Required | Example |
|----------|----------|---------|
| OPENROUTER_API_KEY | ✅ | `sk-or-v1-...` |
| SUPABASE_URL | ✅ | `https://xxx.supabase.co` |
| SUPABASE_KEY | ✅ | `eyJ...` |
| OPENROUTER_BASE_URL | ❌ | `https://openrouter.io/api/v1` |
| LLM_MODEL | ❌ | `openai/gpt-3.5-turbo` |
| EMBEDDING_MODEL | ❌ | `openai/text-embedding-3-small` |
| SESSION_TIMEOUT | ❌ | `3600` |
| MAX_CONTEXT_HISTORY | ❌ | `10` |

## Project Structure

```
agentic_chatbot/
├── app/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── chatbot.py
│   │   └── ...
│   ├── tools/
│   │   ├── __init__.py
│   │   └── core_tools.py
│   ├── main.py
│   ├── config.py
│   ├── embeddings.py
│   ├── session.py
│   ├── knowledge_base.py
│   └── knowledge_base.json
├── requirements.txt
├── .env
├── .gitignore
├── render.yaml
└── README.md
```

## Troubleshooting

### 503 Service Unavailable
- Check Render logs: `Dashboard → Logs`
- Verify all environment variables are set
- Check OpenRouter API key validity
- Verify Supabase connection

### Embeddings Not Working
- Verify OPENROUTER_API_KEY is correct
- Check OpenRouter account has available credits
- Review app logs for API errors

### Session Persistence Issues
- Verify SUPABASE_URL and SUPABASE_KEY
- Check Supabase tables exist and have correct schema
- Review Supabase activity logs

## Support

For issues:
1. Check logs: `Dashboard → Logs`
2. Verify all credentials are correct
3. Test locally: `uvicorn app.main:app --reload`

## License

MIT
