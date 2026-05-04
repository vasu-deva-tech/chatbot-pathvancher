# 🔗 Google Sheets Integration Quick Start

## ✅ What's Ready

**Service Account**: ✓ Already in your project
- File: `agentic_chatbot/google_service_account.json`
- Project: `chatbot-autoresponder-494805`
- Email: `my-back-end-service@chatbot-autoresponder-494805.iam.gserviceaccount.com`

**Code**: ✓ Google Sheets module created
- File: `agentic_chatbot/app/google_sheets.py`
- Functions: Init, KB loader, Response logger, Session storage

**Dependencies**: ✓ Updated requirements.txt
- gspread, google-auth, google-auth-oauthlib

---

## 🚀 3-Step Quick Start

### Step 1: Create Google Sheet (2 minutes)

1. Go to: https://sheets.google.com
2. Click **"+ New"** → **"Blank spreadsheet"**
3. Name it: `Pathvancer Chatbot KB`
4. **Copy the Spreadsheet ID** from URL:
   ```
   https://docs.google.com/spreadsheets/d/[THIS_IS_YOUR_ID]/edit
   ```

### Step 2: Set Up 3 Worksheets

**Sheet 1 - "QA Pairs" (Knowledge Base)**
```
Headers (Row 1):
| Question | Answer | Category | Tags |

Example data:
| What is your product? | We provide AI chatbot solutions | Products | chatbot,ai |
| How to contact? | Email: support@pathvancer.com | Support | contact |
```

**Sheet 2 - "Chat Logs"**
```
Leave empty - headers auto-create when chatbot runs
(Will log all chat responses here automatically)
```

**Sheet 3 - "Sessions"**
```
Leave empty - headers auto-create when chatbot runs
(Will track user sessions automatically)
```

### Step 3: Share with Service Account

1. Click **"Share"** button (top right)
2. Add this email:
   ```
   my-back-end-service@chatbot-autoresponder-494805.iam.gserviceaccount.com
   ```
3. Select **"Editor"** access
4. Click **"Share"**

---

## 📋 Configuration Steps

### Add to `app/config.py`:

```python
# Google Sheets Configuration
GOOGLE_SHEETS_ENABLED = bool(os.getenv("GOOGLE_SHEETS_ENABLED", "True"))
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
GOOGLE_SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "google_service_account.json")
GOOGLE_SHEETS_QA_SHEET = "QA Pairs"
GOOGLE_SHEETS_LOGS_SHEET = "Chat Logs"
GOOGLE_SHEETS_SESSIONS_SHEET = "Sessions"
```

### Add to `.env` (Local Development):

```env
GOOGLE_SHEETS_ENABLED=True
GOOGLE_SHEETS_SPREADSHEET_ID=YOUR_SPREADSHEET_ID_HERE
GOOGLE_SERVICE_ACCOUNT_PATH=agentic_chatbot/google_service_account.json
```

### Add to Render Dashboard (Production):

1. Go to Render → Your Service → Settings → Environment
2. Add variables:

```
GOOGLE_SHEETS_ENABLED=True
GOOGLE_SHEETS_SPREADSHEET_ID=YOUR_SPREADSHEET_ID
GOOGLE_SERVICE_ACCOUNT_PATH=/etc/secrets/google_service_account.json
```

3. Upload file: Settings → Secrets → Add `google_service_account.json`

---

## 🧪 Test Connection

### Local Test

```bash
cd agentic_chatbot
python -c "
from app.google_sheets import init_google_sheets, get_kb_sheets

# Initialize with your spreadsheet ID
init_google_sheets(
    'google_service_account.json',
    'YOUR_SPREADSHEET_ID'
)

# Test KB loading
kb = get_kb_sheets()
pairs = kb.get_qa_pairs()
print(f'✓ Loaded {len(pairs)} Q&A pairs')
"
```

### Expected Output:
```
✓ Google Sheets connected successfully
✓ Opened spreadsheet by ID: [YOUR_ID]
✓ Accessed worksheet: QA Pairs
✓ Loaded X Q&A pairs from Google Sheets
```

---

## 📊 Your Spreadsheet URL

Once created, share this link with your team:
```
https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit
```

Everyone with the link can view and edit the knowledge base.

---

## 🔐 Security Checklist

- [x] Service account JSON in project (`google_service_account.json`)
- [x] Added to `.gitignore` (won't be pushed to GitHub)
- [x] Service account email shared with spreadsheet
- [ ] Environment variable `GOOGLE_SHEETS_SPREADSHEET_ID` set
- [ ] Tested connection locally
- [ ] For Render: Upload as secret file

---

## ✨ Features After Setup

### Knowledge Base
- Load Q&A pairs directly from Google Sheets
- Update knowledge base without redeploying
- Support for categories and tags

### Chat Logging
- Automatic response logging for analytics
- Track: user, message, response, confidence
- Ready for reporting and analysis

### Session Tracking
- Monitor active sessions
- Session analytics automatically recorded
- Easy to generate reports

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Permission denied" | Check service account email is shared with Editor access |
| "Spreadsheet not found" | Verify Spreadsheet ID from URL (no extra spaces) |
| "No Q&A pairs loading" | Check "QA Pairs" sheet exists and has data rows |
| Module error | Run: `pip install gspread google-auth` |

---

**Google Sheets integration is ready to go!** 🎉
