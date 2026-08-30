# Vera Bot Deployment Guide

## Overview

Your Vera Bot is a fully functional AI chatbot backend that handles merchant engagement via WhatsApp. The bot implements all 5 required endpoints and is ready for deployment to a public URL.

### Implemented Endpoints

- ✅ `GET /v1/healthz` — Health check with context load counts
- ✅ `GET /v1/metadata` — Team and bot metadata
- ✅ `POST /v1/context` — Accept category, merchant, customer, and trigger contexts
- ✅ `POST /v1/tick` — Compose messages based on available triggers
- ✅ `POST /v1/reply` — Handle merchant/customer replies with intelligent response logic

### Key Features

**Context Management**:
- Thread-safe storage of category, merchant, customer, and trigger contexts
- Versioning support with idempotency (409 on stale versions)
- Atomic updates for multi-context scenarios

**Message Composition**:
- Trigger-kind dispatch (research_digest, perf_spike, recall_due, dormant_with_vera)
- Context-aware message generation using merchant name, category, performance data
- Merchant-signal alignment (e.g., high-risk-adult cohort for dentists)
- Source attribution and credibility maintenance

**Reply Intelligence**:
- Auto-reply detection (WhatsApp Business canned responses)
- Hard opt-out detection and conversation ending
- Out-of-scope request routing (e.g., GST/tax questions)
- Affirmative engagement detection with contextual follow-ups

**Suppression & Deduplication**:
- Suppression key tracking to prevent duplicate sends
- Conversation-level tracking for ended conversations
- Automatic wait-and-retry for auto-replies (4-hour backoff)

---

## Local Testing (Completed ✓)

Your bot has been tested locally with all 5 endpoints working correctly:

```bash
# Terminal 1: Start the bot
cd d:\magicpin-ai-challenge
py bot.py

# Terminal 2: Test endpoints
# GET /v1/healthz
curl http://localhost:8080/v1/healthz

# GET /v1/metadata
curl http://localhost:8080/v1/metadata

# POST /v1/context, /v1/tick, /v1/reply
# (See test examples in examples/api-call-examples.md)
```

---

## Deployment Options

### Option 1: Railway.app (Recommended for Beginners)

Railway is a simple cloud platform with a free tier that works great for this bot.

**Steps**:

1. Create a Railway account at https://railway.app
2. Create a new project and connect your GitHub repo (or upload files directly)
3. Create `Procfile` in root:
   ```
   web: py bot.py
   ```
4. Set environment variable: `PORT=8080` (Railway will assign this)
5. Deploy and get your public URL: `https://your-project.up.railway.app`

**Update bot.py** to use Railway's PORT environment variable:
```python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
```

### Option 2: Replit.com

**Steps**:

1. Go to https://replit.com
2. Create new Replit project, upload your files
3. Click "Run" — Replit auto-detects Flask and starts the server
4. Your bot gets a public URL: `https://replit-project-name.replit.dev`

### Option 3: Docker + Heroku / Cloud Run / AWS

**Create `Dockerfile`**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY bot.py .
CMD ["python", "bot.py"]
```

**Heroku deployment** (if using Heroku):
```bash
heroku create your-bot-name
git push heroku main
heroku open /v1/healthz
```

### Option 4: ngrok (For Local Testing)

If you want to test locally with a public URL:

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8080

# ngrok gives you: https://xxxx-xx-xxx-xxx-xx.ngrok.io
# Use this URL for testing
```

---

## Production Checklist Before Submitting

- [ ] Bot is running on a public URL
- [ ] All 5 endpoints are accessible from the internet
- [ ] `/v1/healthz` returns `{"status": "ok"}`
- [ ] `/v1/metadata` returns team info
- [ ] `/v1/context` accepts contexts with correct versioning
- [ ] `/v1/tick` composes messages for available triggers
- [ ] `/v1/reply` handles merchant responses intelligently
- [ ] Logs are working (check deployment logs for errors)
- [ ] Bot is running on production WSGI server (not Flask dev server for production)

---

## Production WSGI Server Setup (Recommended)

For production, use **Gunicorn** instead of Flask's development server:

**Update `requirements.txt`**:
```
flask==3.0.0
Werkzeug==3.0.1
gunicorn==21.2.0
```

**Update `Procfile` for Railway/Heroku**:
```
web: gunicorn bot:app
```

**Local test with gunicorn**:
```bash
pip install gunicorn
gunicorn bot:app --bind 0.0.0.0:8080
```

---

## Sample Submission Info

Once deployed, provide the judge with:

```
BOT_URL: https://your-bot-name.up.railway.app
(or your chosen hosting provider's URL)

Endpoints verified live:
- GET /v1/healthz ✓
- GET /v1/metadata ✓
- POST /v1/context ✓
- POST /v1/tick ✓
- POST /v1/reply ✓
```

---

## Troubleshooting

### "Connection refused" on localhost:8080

Bot server isn't running. Start it with:
```bash
py bot.py
```

### 400 Bad Request on /v1/context

JSON payload might be too large or malformed. Check:
- JSON is valid (use `curl -H "Content-Type: application/json" ...`)
- Depth not exceeding 20 levels
- String encoding is UTF-8

### Port already in use

Change port in bot.py:
```python
app.run(host="0.0.0.0", port=9000, debug=False)
```

### Public URL not responding

Check:
1. Deployment logs for startup errors
2. Firewall/network settings allow port 8080
3. Bot is actually running (`curl https://your-url/v1/healthz`)

---

## Next Steps

1. **Choose a deployment platform** from the options above
2. **Update bot.py** to use `os.environ.get("PORT")` for dynamic port binding
3. **Deploy** using the platform's instructions
4. **Test** all endpoints from the public URL
5. **Submit** your bot URL to the challenge judge

Good luck! 🚀
