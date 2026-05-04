# 📋 YOUR SETUP CHECKLIST & RENDER DEPLOYMENT

## ✅ Your Google Sheet Details

**Spreadsheet ID**: `1sGRaQnWOev7Hz0Lw2fTZXV_YxRb1AxNy9t5s5qOlSsQ`

**URL**: https://docs.google.com/spreadsheets/d/1sGRaQnWOev7Hz0Lw2fTZXV_YxRb1AxNy9t5s5qOlSsQ/edit

---

## 📝 CHANGES TO MAKE

### 1. Share Spreadsheet with Service Account

1. Go to your Google Sheet
2. Click **"Share"** (top right)
3. Add: `my-back-end-service@chatbot-autoresponder-494805.iam.gserviceaccount.com`
4. Grant **"Editor"** access
5. Click **"Share"**

✅ **Status**: Pending

### 2. Add Sample Q&A Data to "QA Pairs" Sheet

Add these rows:

```
Question | Answer | Category | Tags
What is Pathvancer? | Pathvancer is an AI-powered business automation platform | Products | platform,ai
What services do you offer? | We offer chatbot solutions and AI integration | Services | services,ai
How can I contact support? | Email: support@pathvancer.com | Support | contact,support
```

✅ **Status**: Pending

### 3. Code Updates (Already Done ✅)

- [x] Google Sheets module created: `app/google_sheets.py`
- [x] Updated `app/config.py` with Google Sheets configuration
- [x] Updated `requirements.txt` with gspread dependencies
- [x] Updated `.gitignore` to exclude service account JSON
- [x] Code pushed to GitHub without exposing secrets

---

## 🚀 RENDER ENVIRONMENT VARIABLES

### Copy These 18 Variables to Render Dashboard

**Path**: dashboard.render.com → Your Service → Settings → Environment

**Your Specific Variables:**

```
OPENROUTER_API_KEY=sk-or-v1-YOUR-API-KEY-HERE
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key-here
GOOGLE_SHEETS_ENABLED=True
GOOGLE_SHEETS_SPREADSHEET_ID=1sGRaQnWOev7Hz0Lw2fTZXV_YxRb1AxNy9t5s5qOlSsQ
GOOGLE_SERVICE_ACCOUNT_PATH=/etc/secrets/google_service_account.json
OPENROUTER_BASE_URL=https://openrouter.io/api/v1
LLM_MODEL=openai/gpt-3.5-turbo
EMBEDDING_MODEL=openai/text-embedding-3-small
SUPABASE_TABLE_SESSIONS=sessions
SUPABASE_TABLE_MESSAGES=messages
PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO
SESSION_TIMEOUT=3600
MAX_CONTEXT_HISTORY=10
HTTP_REFERER=https://pathvancer.com
X_TITLE=PathVancer Chatbot
```

---

## 📋 Quick Reference Table

| # | Variable | Your Value |
|----|----------|-----------|
| 1 | OPENROUTER_API_KEY | sk-or-v1-YOUR-API-KEY-HERE |
| 2 | SUPABASE_URL | https://your-project-id.supabase.co |
| 3 | SUPABASE_KEY | your-service-role-key-here |
| 4 | GOOGLE_SHEETS_ENABLED | True |
| 5 | GOOGLE_SHEETS_SPREADSHEET_ID | 1sGRaQnWOev7Hz0Lw2fTZXV_YxRb1AxNy9t5s5qOlSsQ |
| 6 | GOOGLE_SERVICE_ACCOUNT_PATH | /etc/secrets/google_service_account.json |
| 7 | OPENROUTER_BASE_URL | https://openrouter.io/api/v1 |
| 8 | LLM_MODEL | openai/gpt-3.5-turbo |
| 9 | EMBEDDING_MODEL | openai/text-embedding-3-small |
| 10 | SUPABASE_TABLE_SESSIONS | sessions |
| 11 | SUPABASE_TABLE_MESSAGES | messages |
| 12 | PORT | 8000 |
| 13 | ENVIRONMENT | production |
| 14 | LOG_LEVEL | INFO |
| 15 | SESSION_TIMEOUT | 3600 |
| 16 | MAX_CONTEXT_HISTORY | 10 |
| 17 | HTTP_REFERER | https://pathvancer.com |
| 18 | X_TITLE | PathVancer Chatbot |

---

## 🔐 Upload Google Service Account to Render

1. In Render Dashboard, go to **Settings → Secrets** (bottom)
2. Click **"Add Secret"**
3. **File name**: `google_service_account.json`
4. **Content**: Copy-paste the entire content from your `chatbot-autoresponder-494805-b35a8061c208.json` file
5. Click **"Add"**

---

## ✅ DEPLOYMENT CHECKLIST

### Before Deploying:
- [ ] Shared spreadsheet with service account email
- [ ] Added 3 Q&A rows to "QA Pairs" sheet
- [ ] Local .env updated with Spreadsheet ID
- [ ] All 18 environment variables added to Render
- [ ] Google service account JSON uploaded as Render secret

### After Deploying:
- [ ] Check Render logs for initialization message
- [ ] Test /health endpoint
- [ ] Send test chat message
- [ ] Verify responses logged to Google Sheets

---

## 🎯 WHAT YOU NOW HAVE

✅ **LangChain Agent** with 6 tools
✅ **OpenRouter API** for LLM + Embeddings
✅ **Supabase** for session storage
✅ **Google Sheets** for KB + logging + analytics
✅ **Render Ready** - All code on GitHub
✅ **Security** - No secrets exposed

---

## 📱 Your Spreadsheet

**URL**: https://docs.google.com/spreadsheets/d/1sGRaQnWOev7Hz0Lw2fTZXV_YxRb1AxNy9t5s5qOlSsQ/edit

**Worksheets**:
- `QA Pairs` - Your knowledge base
- `Chat Logs` - Auto-populated responses
- `Sessions` - Auto-populated session data

---

## 🚀 NEXT STEPS

1. Share spreadsheet (5 min)
2. Add sample Q&A (2 min)
3. Add Render environment variables (5 min)
4. Upload Google service account (1 min)
5. Deploy and test (2 min)

**Total time: ~15 minutes!**

---

**Ready to deploy?** 🎉
