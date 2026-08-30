# Vera Bot — Quick Reference & Deployment Guide

## Quick Start (Local Testing)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Bot Locally
```bash
python3 bot.py
```

Expected output:
```
* Running on http://127.0.0.1:5000
* Debug mode: off
```

### 3. Test Endpoints (in another terminal)
```bash
# Health check
curl http://localhost:5000/v1/healthz

# Bot metadata
curl http://localhost:5000/v1/metadata

# Accept a merchant context
curl -X POST http://localhost:5000/v1/context \
  -H "Content-Type: application/json" \
  -d '{"scope":"merchant","context_id":"m1","version":1,"payload":{}}'

# Compose messages
curl -X POST http://localhost:5000/v1/tick \
  -H "Content-Type: application/json" \
  -d '{"now":"2025-01-01T12:00:00Z","available_triggers":[]}'

# Handle reply
curl -X POST http://localhost:5000/v1/reply \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"c1","merchant_id":"m1","message":"interested"}'
```

---

## Replit Deployment (3 Steps)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Vera bot ready"
git push origin main
```

### Step 2: Import to Replit
1. Go to https://replit.com/new
2. Click "Import from GitHub"
3. Paste your GitHub URL
4. Click "Import"
5. Replit auto-configures everything

### Step 3: Share Endpoint
1. Wait for bot to start (see "Running on http://0.0.0.0:5000")
2. Click "Share" → Copy public URL
3. **Your bot is live!**

Example endpoint: `https://vera-bot-challenge.replit.dev`

---

## Verify Endpoints Are Working

### Quick Test (cURL)
```bash
BASE_URL="https://your-replit.replit.dev"

curl $BASE_URL/v1/healthz
curl $BASE_URL/v1/metadata
curl -X POST $BASE_URL/v1/context -H "Content-Type: application/json" -d '{"scope":"merchant","context_id":"m1","version":1,"payload":{}}'
```

### Full Test (judge_simulator.py)
```bash
python3 judge_simulator.py
```

Input: Your Replit endpoint URL
Output: Test results (expected 13/13 pass)

---

## Files Overview

| File | Purpose | Status |
|------|---------|--------|
| `bot.py` | Main bot logic (570 lines) | ✅ Hardened |
| `requirements.txt` | Python dependencies | ✅ Updated |
| `Procfile` | Cloud deployment config | ✅ Fixed |
| `.replit` | Replit configuration | ✅ Added |
| `runtime.txt` | Python version spec | ✅ Added |
| `.env.example` | Environment variables | ✅ Added |
| `README.md` | Project documentation | ✅ Complete |
| `HARDENING_AUDIT.md` | Issues fixed | ✅ Complete |
| `CHALLENGE_SUMMARY.md` | Challenge overview | ✅ Complete |
| `SUBMISSION_CHECKLIST.md` | Pre-submission steps | ✅ Complete |
| `dataset/` | 50M, 200C, 100T | ✅ Included |

---

## Hardening Summary

✅ **Fixed 6 Major Issues**:
1. datetime.utcnow() → datetime.now(timezone.utc)
2. Procfile: py → python3
3. Added gunicorn to requirements.txt
4. JSON error handling on all POST endpoints
5. Replit configuration files (.replit, runtime.txt)
6. Environment variable documentation

✅ **Result**: Production-ready, Linux-compatible, Replit-optimized

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Bot won't start | Check Python version (3.11+), run `pip install -r requirements.txt` |
| Port 5000 in use | Replit auto-assigns different port, no action needed |
| JSON parse error | Ensure valid JSON in POST body, include Content-Type header |
| Endpoints return 500 | Check Replit console for error, verify context was loaded |
| Timeout errors | Increase timeout to 10s, check bot is running on Replit |
| Deprecated datetime | ✅ Already fixed in this version |

---

## Submission Info

**What to Submit**:
- **Endpoint URL**: https://your-replit.replit.dev
- **5 Endpoints**: healthz, metadata, context, tick, reply
- **Team Name**: Vera Bot Challenge Team
- **Framework**: Flask 3.0.0
- **Language**: Python 3.11

**Success Criteria**:
- ✅ All 5 endpoints live and responding
- ✅ Judge simulator: 13/13 tests passing
- ✅ No timeouts or errors
- ✅ Messages are contextual (merchant-aware)
- ✅ Reply intelligence working (not generic)

---

## File Structure
```
magicpin-ai-challenge/
├── bot.py                      # Main bot (hardened)
├── judge_simulator.py          # Judge test script
├── requirements.txt            # Dependencies (with gunicorn)
├── Procfile                    # Cloud config (python3)
├── .replit                     # Replit config (NEW)
├── runtime.txt                 # Python version (NEW)
├── .env.example                # Env vars (NEW)
├── README.md                   # Quick start
├── HARDENING_AUDIT.md          # Issues fixed (NEW)
├── CHALLENGE_SUMMARY.md        # Challenge overview (NEW)
├── SUBMISSION_CHECKLIST.md     # Pre-submission steps (NEW)
├── dataset/
│   ├── customers_seed.json
│   ├── merchants_seed.json
│   ├── triggers_seed.json
│   └── categories/
│       ├── dentists.json
│       ├── gyms.json
│       ├── pharmacies.json
│       ├── restaurants.json
│       └── salons.json
└── examples/
    ├── api-call-examples.md
    └── case-studies.md
```

---

## Key Endpoints at a Glance

### GET /v1/healthz
- **Purpose**: Health check + context count
- **Returns**: `{status, uptime_seconds, contexts_loaded}`
- **Example**:
  ```bash
  curl https://bot.replit.dev/v1/healthz
  ```

### GET /v1/metadata
- **Purpose**: Team info + approach
- **Returns**: `{team_name, model, approach, version, submitted_at}`
- **Example**:
  ```bash
  curl https://bot.replit.dev/v1/metadata
  ```

### POST /v1/context
- **Purpose**: Store versioned contexts (category, merchant, customer, trigger)
- **Returns**: `{accepted, ack_id, stored_at}` (200) or error (409/400/500)
- **Example**:
  ```bash
  curl -X POST https://bot.replit.dev/v1/context \
    -H "Content-Type: application/json" \
    -d '{
      "scope": "merchant",
      "context_id": "merchant_001",
      "version": 1,
      "payload": {
        "identity": {"owner_first_name": "Dr. Smith"},
        "performance": {"views": 1500},
        "subscription": {"status": "active"}
      }
    }'
  ```

### POST /v1/tick
- **Purpose**: Compose messages for available triggers
- **Returns**: `{actions: [{message_action_dict}]}`
- **Example**:
  ```bash
  curl -X POST https://bot.replit.dev/v1/tick \
    -H "Content-Type: application/json" \
    -d '{
      "now": "2025-01-15T10:30:00Z",
      "available_triggers": ["trigger_001", "trigger_002"]
    }'
  ```

### POST /v1/reply
- **Purpose**: Handle merchant/customer replies
- **Returns**: `{action: "send|wait|end", body, rationale}`
- **Example**:
  ```bash
  curl -X POST https://bot.replit.dev/v1/reply \
    -H "Content-Type: application/json" \
    -d '{
      "conversation_id": "conv_m001",
      "merchant_id": "merchant_001",
      "message": "yes, tell me more",
      "from_role": "merchant"
    }'
  ```

---

## Success Checklist

Before submitting to judge:

- [ ] Bot runs locally without errors: `python3 bot.py`
- [ ] All 5 endpoints respond: `curl http://localhost:5000/v1/...`
- [ ] Bot deployed to Replit: GitHub → Import → Run
- [ ] Replit endpoint is live and accessible
- [ ] Judge simulator passes 13/13 tests
- [ ] Dataset loaded (50M, 200C, 100T)
- [ ] No warnings in Replit console
- [ ] Endpoint URL ready for submission

---

## Emergency Troubleshooting

**Bot won't start**:
```bash
python3 -m py_compile bot.py  # Check syntax
pip install -r requirements.txt  # Install deps
python3 bot.py --debug  # Run with debug
```

**Endpoint returns 500**:
1. Check Replit console for traceback
2. Verify JSON payload is valid
3. Ensure context was loaded (POST /v1/context)
4. Check bot is still running

**Judge simulator fails**:
1. Verify endpoint URL is correct
2. Test manually: `curl https://endpoint/v1/healthz`
3. Check internet connection
4. Restart bot on Replit

---

## Final Notes

- ✅ Bot is fully hardened for Linux/Replit
- ✅ All 5 endpoints implemented and tested
- ✅ 50 merchants, 200 customers, 100 triggers ready
- ✅ Intelligent message composition working
- ✅ Reply patterns detected accurately
- ✅ Ready for judge evaluation

**Next Action**: Deploy to Replit and submit endpoint URL!
