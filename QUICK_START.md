# Quick Start Guide — Vera Bot

## 🎯 What You Have

A fully functional Vera bot backend with all 5 required endpoints:
- ✅ `GET /v1/healthz` — Health check
- ✅ `GET /v1/metadata` — Bot info
- ✅ `POST /v1/context` — Accept contexts
- ✅ `POST /v1/tick` — Compose messages
- ✅ `POST /v1/reply` — Handle replies

**Status**: Tested locally, ready for production deployment

---

## ⚡ Quick Start (5 minutes)

### Step 1: Deploy to Railway.app (Easiest)

1. Visit https://railway.app and sign up
2. Create new project → connect GitHub repo (or upload files)
3. Railway auto-detects Procfile and deploys
4. Get your public URL (e.g., `https://vera-bot-xyz.railway.app`)
5. Test it:
   ```bash
   curl https://vera-bot-xyz.railway.app/v1/healthz
   ```

### Step 2: Alternative — Deploy to Replit.com

1. Visit https://replit.com
2. Create new Replit, upload your bot files
3. Click "Run"
4. Replit gives you a public URL (e.g., `https://vera-bot.replit.dev`)
5. Done! 🎉

### Step 3: Test All Endpoints

Use Postman or curl:

```bash
# Health check
curl https://your-bot-url/v1/healthz

# Metadata
curl https://your-bot-url/v1/metadata

# Push a category context
curl -X POST https://your-bot-url/v1/context \
  -H "Content-Type: application/json" \
  -d '{"scope":"category", "context_id":"dentists", "version":1, "payload":{...}}'

# Tick for messages
curl -X POST https://your-bot-url/v1/tick \
  -H "Content-Type: application/json" \
  -d '{"now":"2026-08-30T12:00:00Z", "available_triggers":["trg_001"]}'

# Reply to message
curl -X POST https://your-bot-url/v1/reply \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"conv_...", "message":"Yes please!", "from_role":"merchant"}'
```

### Step 4: Submit to Judge

Provide your bot URL:
```
Bot URL: https://your-bot-xyz.railway.app
Status: All 5 endpoints live and tested ✓
```

---

## 📋 What's in the Box

```
d:\magicpin-ai-challenge\
├── bot.py                          # Main bot (570 lines, ready to deploy)
├── requirements.txt                # Dependencies (flask, werkzeug)
├── Procfile                        # Cloud deployment config
├── DEPLOYMENT.md                   # Detailed deployment guide
├── TEST_RESULTS.md                 # Full test results
├── QUICK_START.md                  # This file
├── dataset/
│   └── expanded/
│       ├── categories/             # 5 category contexts
│       ├── merchants/              # 50 merchant contexts
│       ├── customers/              # 200 customer contexts
│       ├── triggers/               # 100 trigger contexts
│       └── test_pairs.json         # 30 test pairs
├── examples/
│   └── api-call-examples.md        # Request/response examples
└── challenge-*.md                  # Challenge specification
```

---

## 🧪 Local Testing (Optional)

Run locally before deploying:

```bash
# Terminal 1: Start bot
cd d:\magicpin-ai-challenge
py -m pip install flask
py bot.py

# Terminal 2: Test
curl http://localhost:8080/v1/healthz
```

---

## 🚀 Recommended Deployment Path

1. **Quick Path (10 min)**: Railway.app
   - Simplest setup
   - Auto-deploys from Git
   - Free tier sufficient
   - Public URL in 2 clicks

2. **Beginner Path (15 min)**: Replit.com
   - No CLI needed
   - Auto-detects Python
   - Web IDE included
   - Great for learning

3. **Advanced Path (30 min)**: Docker + Cloud Run
   - More control
   - Better for production scale
   - Requires Docker knowledge

---

## ✅ Pre-Deployment Checklist

Before submitting:
- [ ] Bot runs locally: `py bot.py` → starts on 8080
- [ ] `GET /v1/healthz` returns `{"status": "ok"}`
- [ ] `GET /v1/metadata` returns team info
- [ ] Deployed to Railway/Replit/etc.
- [ ] All 5 endpoints accessible from the internet
- [ ] Responses match expected format
- [ ] No errors in deployment logs

---

## 🎓 Understanding the Bot

### How It Works

1. **Judge pushes contexts** → `/v1/context` endpoint stores them
2. **Judge calls tick** → `/v1/tick` endpoint composes message from available triggers
3. **Judge sends message to merchant** → merchant replies
4. **Judge sends reply** → `/v1/reply` endpoint processes it and decides follow-up
5. **Cycle repeats** until conversation ends

### Key Features

**Smart Reply Handling**:
- Detects WhatsApp auto-replies → backs off 4 hours
- Detects hard opt-out → ends conversation gracefully
- Detects affirmative → follows up with contextual action
- Detects out-of-scope → redirects politely

**Message Composition**:
- Looks up merchant's category, performance, signals
- Matches trigger kind to handler (research, perf_spike, recall, etc.)
- Generates merchant-aware, contextual messages
- Includes rationale for every decision

**De-duplication**:
- Tracks suppression keys (no duplicate sends of same trigger)
- Tracks ended conversations (won't send to opted-out merchants)
- Idempotent context endpoints (safe to re-push same version)

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Bot not running. Run `py bot.py` |
| "Module not found" (flask) | Install: `pip install flask` |
| Port 8080 already in use | Change port in bot.py or kill process using port |
| Deployment fails | Check logs on Railway/Replit dashboard |
| 400 Bad Request | Check JSON payload format (must be valid UTF-8) |
| 409 Conflict on /v1/context | You're pushing a stale version (use newer version) |

---

## 📞 Support

- **Endpoint docs**: See `examples/api-call-examples.md`
- **Context structure**: See `challenge-brief.md`
- **Full test results**: See `TEST_RESULTS.md`
- **Deployment help**: See `DEPLOYMENT.md`

---

## 🎉 You're Ready!

Your bot is fully built and tested. Now just deploy it and submit the URL. Good luck! 🚀
