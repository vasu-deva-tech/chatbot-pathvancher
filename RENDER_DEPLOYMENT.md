# Render Deployment Guide - Pathvancer Chatbot

## Prerequisites Checklist

- ✅ GitHub Repository: `https://github.com/vasu-deva-tech/chatbot-pathvancher.git`
- ✅ Supabase Project: Tables in `chatbot` database
- ✅ Render Account: [render.com](https://render.com)
- ✅ OpenRouter API Key
- ✅ Supabase Keys

---

## Step 1: Prepare Supabase Database

### Create Tables in Supabase

Go to your Supabase project → SQL Editor and run:

```sql
-- Create sessions table
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

-- Create messages table
CREATE TABLE messages (
  id BIGSERIAL PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_last_activity ON sessions(last_activity);
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

### Get Your Credentials

1. Go to **Settings → API** in Supabase
2. Copy these values:
   - **Project URL**: `SUPABASE_URL` (e.g., `https://jqpwiuomjczspofgopcm.supabase.co`)
   - **Service Role Secret**: `SUPABASE_KEY` (use this for server-side, starts with `eyJ...`)

---

## Step 2: Push Code to GitHub

Make sure all files are in your GitHub repository:

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

Required files:
- ✅ `app/` folder with all Python files
- ✅ `requirements.txt`
- ✅ `.env.example` (without sensitive keys)
- ✅ `render.yaml` (deployment config)
- ✅ `README.md`

---

## Step 3: Manual Deployment on Render

### 3.1 Create a New Web Service

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** button (top-right)
3. Select **"Web Service"**

### 3.2 Connect Your GitHub Repository

1. Click **"Connect account"** next to GitHub
2. Authorize Render to access your GitHub
3. Select repository: `chatbot-pathvancher`
4. Select branch: `main`

### 3.3 Configure Service

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `pathvancer-chatbot` |
| **Environment** | `Python 3.11` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Starter` (or `Standard` for better performance) |

### 3.4 Add Environment Variables

In the **"Environment"** section, click **"Add Environment Variable"** for each:

```
OPENROUTER_API_KEY=sk-or-v1-YOUR-API-KEY-HERE

SUPABASE_URL=https://your-project-id.supabase.co

SUPABASE_KEY=your-service-role-key-here

OPENROUTER_BASE_URL=https://openrouter.io/api/v1

LLM_MODEL=openai/gpt-3.5-turbo

EMBEDDING_MODEL=openai/text-embedding-3-small

SESSION_TIMEOUT=3600

MAX_CONTEXT_HISTORY=10

ENVIRONMENT=production

LOG_LEVEL=INFO

SUPABASE_TABLE_SESSIONS=sessions

SUPABASE_TABLE_MESSAGES=messages
```

### 3.5 Review & Deploy

1. Scroll down to **"Create Web Service"** button
2. Click it - Render will start building and deploying
3. Watch the logs for any errors

---

## Step 4: Monitor Deployment

### During Build

- Render will clone your repo
- Install dependencies from `requirements.txt`
- Start the application

### Check Logs

In Render dashboard:
1. Click on your service `pathvancer-chatbot`
2. Go to **"Logs"** tab
3. Look for message: `✓ All services initialized successfully (using OpenRouter + Supabase)`

### Get Your Live URL

Once deployed, you'll see:
- **Live URL**: `https://pathvancer-chatbot.onrender.com`
- Use this to test your API

---

## Step 5: Test Your Deployment

### Test Health Check

```bash
curl https://pathvancer-chatbot.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "embeddings_ready": true,
  "agent_ready": true
}
```

### Test Chat Endpoint

```bash
curl -X POST https://pathvancer-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what can you help with?",
    "session_id": "test-session-001",
    "user_id": "test-user-001"
  }'
```

### Test Session Retrieval

```bash
curl https://pathvancer-chatbot.onrender.com/session/test-session-001
```

---

## Troubleshooting

### Build Fails: "ModuleNotFoundError"

**Problem**: Missing Python dependencies
**Solution**: Ensure all imports in your code are in `requirements.txt`

```bash
# Check and update requirements
pip freeze > requirements.txt
git push
```

### 503 Service Unavailable

**Problem**: Application crashed after deployment
**Check**:
1. Logs show error during startup
2. Environment variables not set correctly
3. OpenRouter API key invalid
4. Supabase connection failed

**Debug**:
```bash
# In Render logs, look for:
# ❌ OPENROUTER_API_KEY not set
# ❌ Error connecting to Supabase
# ❌ Invalid credentials
```

### "Connection refused" to Supabase

**Problem**: Can't reach Supabase from Render
**Solution**:
1. Verify SUPABASE_URL is correct (should be `https://...`)
2. Verify SUPABASE_KEY is the service role key (not anon key)
3. Check Supabase firewall settings allow external connections

### Embeddings Not Working

**Problem**: 429 errors from OpenRouter
**Cause**: Rate limit or invalid API key
**Solution**:
1. Verify OpenRouter API key is correct
2. Check account has available credits
3. Start with cheaper model: `openai/gpt-3.5-turbo`

---

## Maintenance

### Redeploy After Code Changes

1. Push changes to GitHub:
```bash
git add .
git commit -m "Update chatbot logic"
git push origin main
```

2. Render will auto-redeploy (if auto-deploy enabled)

### Manual Redeploy

In Render dashboard:
- Click your service
- Click **"Manual Deploy"** (top-right)
- Select branch `main`
- Click **"Deploy Latest Commit"`

### Update Environment Variables

1. Click your service in Render
2. Go to **"Environment"** tab
3. Edit variable and click **"Save"**
4. Service auto-restarts with new values

---

## Important Notes

⚠️ **Never commit `.env` file to GitHub** - It contains sensitive keys

✅ **Keep `.env.example`** in repo without real keys - For reference

✅ **Use Render's environment variables** for production - Never hardcode secrets

✅ **Monitor free tier limits** - Render free tier has monthly limits

✅ **Test locally first** - Before pushing to GitHub

---

## Next Steps After Deployment

1. ✅ Verify health check works
2. ✅ Test chat endpoint with sample message
3. ✅ Check Supabase database for saved sessions
4. ✅ Monitor logs for any errors
5. ✅ Share live URL with users

---

## Support

**Render Docs**: https://docs.render.com
**Supabase Docs**: https://supabase.com/docs
**OpenRouter Docs**: https://openrouter.io/docs

For issues, check:
1. Render logs for errors
2. Supabase activity logs
3. OpenRouter API status
