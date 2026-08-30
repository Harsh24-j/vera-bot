# Vera Bot — Merchant AI Assistant for WhatsApp

A production-ready AI chatbot backend that engages merchants via WhatsApp, helping them grow their businesses through personalized, context-aware conversations.

**Status**: ✅ All 5 endpoints implemented, tested, and ready to deploy

---

## 🎯 What is Vera Bot?

Vera is an AI chatbot that:
- 📱 Engages merchants on WhatsApp
- 📊 Provides context-aware recommendations (research, performance metrics, customer insights)
- 🤖 Handles merchant replies intelligently (detects auto-replies, opt-outs, questions)
- 🎯 Maintains conversation state with suppression & de-duplication
- 🔄 Composes category-specific, merchant-aware messages

**Built for**: magicpin AI Challenge — merchant engagement across 5 service categories (dentists, salons, restaurants, gyms, pharmacies)

---

## ✨ Features

### 🔌 5 Required API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/healthz` | GET | Health check + context counts |
| `/v1/metadata` | GET | Bot team info & version |
| `/v1/context` | POST | Accept category/merchant/customer/trigger contexts |
| `/v1/tick` | POST | Compose messages from available triggers |
| `/v1/reply` | POST | Handle merchant/customer replies intelligently |

### 🧠 Intelligent Message Composition

- **Trigger-kind dispatch**: Different handlers for research_digest, perf_spike, recall_due, dormant_with_vera
- **Category awareness**: Vocabulary, tone, and offers tailored to business type
- **Merchant signal alignment**: Recommendations tied to merchant's specific strengths/weaknesses
- **Source attribution**: All research/digest items include credibility markers

### 📨 Smart Reply Handling

- ✅ **Auto-reply detection** → 4-hour backoff for WhatsApp Business auto-replies
- ✅ **Opt-out detection** → Graceful conversation ending
- ✅ **Affirmative engagement** → Contextual follow-up responses
- ✅ **Out-of-scope routing** → Polite redirection for off-topic requests
- ✅ **Question detection** → Engaged, helpful responses

### 🔐 Production Features

- Versioned context storage (409 Conflict on stale versions)
- De-duplication via suppression keys
- Conversation state tracking
- Idempotent endpoints
- Error handling & logging
- Environment variable support

---

## 📦 Project Structure

```
vera-bot/
├── bot.py                    # Main bot backend (570 lines)
├── requirements.txt          # Python dependencies
├── Procfile                  # Cloud deployment config
├── README.md                 # This file
├── QUICK_START.md            # 5-minute getting started
├── DEPLOYMENT.md             # Detailed deployment guide
├── TEST_RESULTS.md           # Full test report (13/13 ✅)
├── IMPLEMENTATION_SUMMARY.md # Architecture & design
├── dataset/
│   ├── generate_dataset.py   # Dataset generator
│   ├── expanded/
│   │   ├── categories/       # 5 category contexts
│   │   ├── merchants/        # 50 merchant contexts
│   │   ├── customers/        # 200 customer contexts
│   │   ├── triggers/         # 100 trigger contexts
│   │   └── test_pairs.json   # 30 test pairs
│   └── [seed files]
└── examples/
    └── api-call-examples.md  # Request/response examples
```

---

## 🚀 Quick Start (5 Minutes)

### Option 1: Deploy on Railway.app (Easiest)

```bash
# 1. Go to https://railway.app
# 2. Create new project → Connect this GitHub repo
# 3. Railway auto-detects Procfile and deploys
# 4. Get public URL: https://vera-bot-xyz.railway.app
# 5. Test: curl https://vera-bot-xyz.railway.app/v1/healthz
```

### Option 2: Deploy on Replit.com

```bash
# 1. Go to https://replit.com
# 2. Create new Replit, upload bot files
# 3. Click "Run"
# 4. Get public URL automatically
```

### Option 3: Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py

# Test endpoints
curl http://localhost:8080/v1/healthz
curl http://localhost:8080/v1/metadata
```

---

## 📋 API Examples

### GET /v1/healthz
```bash
curl http://localhost:8080/v1/healthz
```

**Response**:
```json
{
  "status": "ok",
  "uptime_seconds": 125,
  "contexts_loaded": {
    "category": 1,
    "merchant": 1,
    "trigger": 1,
    "customer": 0
  }
}
```

### GET /v1/metadata
```bash
curl http://localhost:8080/v1/metadata
```

**Response**:
```json
{
  "team_name": "Vera Bot Challenge Team",
  "team_members": ["Bot Builder"],
  "model": "claude-3-5-sonnet-20241022",
  "approach": "Multi-context composer with trigger-kind dispatch",
  "version": "1.0.0",
  "contact_email": "bot@magicpin.ai"
}
```

### POST /v1/context
```bash
curl -X POST http://localhost:8080/v1/context \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "category",
    "context_id": "dentists",
    "version": 1,
    "payload": { /* category data */ }
  }'
```

**Response**:
```json
{
  "accepted": true,
  "ack_id": "ack_dentists_v1",
  "stored_at": "2026-08-30T06:01:23.689190Z"
}
```

### POST /v1/tick
```bash
curl -X POST http://localhost:8080/v1/tick \
  -H "Content-Type: application/json" \
  -d '{
    "now": "2026-08-30T12:00:00Z",
    "available_triggers": ["trg_001_research_digest"]
  }'
```

**Response**:
```json
{
  "actions": [
    {
      "conversation_id": "conv_m_001_...",
      "merchant_id": "m_001_...",
      "send_as": "vera",
      "body": "Dr. Meera, JIDA's Oct issue landed...",
      "cta": "open_ended",
      "suppression_key": "research:dentists:2026-W17",
      "rationale": "External research digest with merchant-relevant clinical anchor..."
    }
  ]
}
```

### POST /v1/reply
```bash
curl -X POST http://localhost:8080/v1/reply \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_m_001_...",
    "merchant_id": "m_001_...",
    "from_role": "merchant",
    "message": "Yes please, send the abstract",
    "received_at": "2026-08-30T12:05:00Z",
    "turn_number": 2
  }'
```

**Response**:
```json
{
  "action": "send",
  "body": "Sending the abstract now...",
  "cta": "open_ended",
  "rationale": "Affirmative engagement detected, following up with contextual response"
}
```

---

## 🧪 Testing

### Local Testing

All 5 endpoints have been tested locally with 13 test scenarios:

| Scenario | Status |
|----------|--------|
| Health check (empty) | ✅ Pass |
| Metadata retrieval | ✅ Pass |
| Accept category context | ✅ Pass |
| Reject stale version (409) | ✅ Pass |
| Accept newer version | ✅ Pass |
| Accept merchant context | ✅ Pass |
| Accept trigger context | ✅ Pass |
| Health check (after load) | ✅ Pass |
| Compose message via tick | ✅ Pass |
| Reply with affirmative | ✅ Pass |
| Detect auto-reply | ✅ Pass |
| Detect hard opt-out | ✅ Pass |
| Return empty actions | ✅ Pass |

**Result**: 13/13 ✅ (100% pass rate)

See `TEST_RESULTS.md` for detailed report.

---

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** — Get running in 5 minutes
- **[DEPLOYMENT.md](DEPLOYMENT.md)** — Detailed deployment for all platforms (Railway, Replit, Docker, etc.)
- **[TEST_RESULTS.md](TEST_RESULTS.md)** — Full test report and scenarios
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** — Architecture & design decisions
- **[examples/api-call-examples.md](examples/api-call-examples.md)** — Complete API request/response examples

---

## 🔧 Technology Stack

- **Framework**: Flask (Python)
- **Language**: Python 3.11+
- **Dependencies**: 
  - flask==3.0.0
  - Werkzeug==3.0.1
- **Deployment**: Railway, Replit, Docker, Cloud Run, Heroku, etc.
- **Hosting**: Cloud-agnostic (any platform supporting Docker/Python)

---

## 💡 Key Architecture

### Context Management
- **BotState**: Versioned storage for category, merchant, customer, trigger contexts
- **Versioning**: Rejects stale versions (409 Conflict), atomically updates
- **Tracking**: Conversation state, ended conversations, suppression keys

### Message Composition
- **Trigger dispatch**: Different handlers for each trigger kind
- **Context lookup**: Finds category knowledge, merchant performance, customer state
- **Smart composition**: Generates merchant-aware, category-specific messages
- **Rationale**: Every action includes reasoning for transparency

### Reply Intelligence
- **Pattern detection**: Auto-reply, opt-out, affirmative, out-of-scope, questions
- **Conversation management**: Tracks ended conversations, prevents spam
- **Context-aware follow-up**: Generates relevant next steps based on merchant state

---

## 📊 Dataset

Includes deterministic, challenge-ready dataset:

- **50 merchants** across 5 categories (dentists, salons, restaurants, gyms, pharmacies)
- **200 customers** distributed across merchants
- **100 triggers** of various kinds (research_digest, perf_spike, recall_due, etc.)
- **30 test pairs** for standardized evaluation
- **5 categories** with voice profiles, offer catalogs, peer stats, digest items, trends

Located in `dataset/expanded/`

---

## 🎯 Submission Checklist

Before submitting to the judge:

- [ ] Bot deployed to public URL (e.g., https://vera-bot-xyz.railway.app)
- [ ] All 5 endpoints accessible from the internet
- [ ] GET /v1/healthz returns 200 with correct structure
- [ ] GET /v1/metadata returns team info
- [ ] POST /v1/context accepts contexts with proper versioning
- [ ] POST /v1/tick composes messages for triggers
- [ ] POST /v1/reply handles replies intelligently
- [ ] Auto-replies detected and backed off (4-hour wait)
- [ ] Opt-out requests respected (conversation ended)
- [ ] All error responses return valid JSON

---

## 🚀 Next Steps

1. **Fork or clone** this repository
2. **Deploy** using Railway.app, Replit, or your preferred platform (see DEPLOYMENT.md)
3. **Get public URL** from your hosting provider
4. **Test endpoints** to ensure all are working
5. **Submit bot URL** to the challenge judge

---

## 📞 Support

- **Deployment help**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **API examples**: See [examples/api-call-examples.md](examples/api-call-examples.md)
- **Architecture**: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Test results**: See [TEST_RESULTS.md](TEST_RESULTS.md)
- **Getting started**: See [QUICK_START.md](QUICK_START.md)

---

## 📄 License

Built for magicpin AI Challenge 2026

---

## ✨ Highlights

✅ **Production-ready** — Error handling, logging, versioning
✅ **Fully tested** — 13/13 scenarios passing locally
✅ **Well-documented** — README, deployment guide, test results, API examples
✅ **Cloud-agnostic** — Deploy anywhere (Railway, Replit, Docker, Cloud Run, etc.)
✅ **Smart composition** — Category-aware, context-driven, trigger-dispatched
✅ **Intelligent replies** — Detects auto-replies, opt-outs, affirmative, out-of-scope
✅ **State management** — Versioned contexts, de-duplication, conversation tracking
✅ **Ready to scale** — WSGI-compatible, environment-variable driven

---

**Your bot is ready to go live. Deploy now and engage merchants! 🚀**
