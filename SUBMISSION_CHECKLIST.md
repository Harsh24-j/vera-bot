# Vera Bot — Final Submission Checklist

## Pre-Submission Verification (Run Locally First)

### ✅ Phase 1: Code & Syntax Validation
- [ ] Bot syntax valid: `python3 -m py_compile bot.py`
- [ ] Requirements file valid: `pip install -r requirements.txt`
- [ ] All imports resolve: No missing dependencies
- [ ] No hardcoded paths or Windows-specific code
- [ ] Logging configured correctly

### ✅ Phase 2: 5 Endpoint Validation (cURL or Postman)

#### 1. GET /v1/healthz
```bash
curl -X GET http://localhost:5000/v1/healthz
# Expected: 200 OK with uptime_seconds and context counts
```
- [ ] Returns 200 status
- [ ] Contains `uptime_seconds` field
- [ ] Contains `contexts_loaded` object with category/merchant/customer/trigger counts

#### 2. GET /v1/metadata  
```bash
curl -X GET http://localhost:5000/v1/metadata
# Expected: 200 OK with team info and approach description
```
- [ ] Returns 200 status
- [ ] Contains `team_name`, `model`, `approach`, `version`
- [ ] Contains `submitted_at` ISO timestamp

#### 3. POST /v1/context (Category)
```bash
curl -X POST http://localhost:5000/v1/context \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "category",
    "context_id": "cat_dentists",
    "version": 1,
    "payload": {"name": "Dentists", "digest": []}
  }'
# Expected: 200 OK with accepted: true, ack_id, stored_at
```
- [ ] Returns 200 for new category
- [ ] Returns 409 for stale version
- [ ] Includes `ack_id` in response
- [ ] Includes `stored_at` timestamp

#### 4. POST /v1/tick (Message Decision)
```bash
curl -X POST http://localhost:5000/v1/tick \
  -H "Content-Type: application/json" \
  -d '{
    "now": "2025-01-01T12:00:00Z",
    "available_triggers": ["trigger_123"]
  }'
# Expected: 200 OK with actions array (may be empty if no context)
```
- [ ] Returns 200 status
- [ ] Returns `actions` array
- [ ] Actions include message fields when triggers available

#### 5. POST /v1/reply (Reply Handling)
```bash
curl -X POST http://localhost:5000/v1/reply \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123",
    "merchant_id": "merc_001",
    "customer_id": "cust_001",
    "message": "interested",
    "from_role": "merchant"
  }'
# Expected: 200 OK with action field (send/wait/end)
```
- [ ] Returns 200 status
- [ ] Returns `action` field (send/wait/end)
- [ ] Auto-reply detection working (wait 4 hours)
- [ ] Opt-out detection working (end conversation)

### ✅ Phase 3: Dataset Verification
```bash
ls -la dataset/expanded/
# Should show:
# - customers_expanded.json (200 customers)
# - merchants_expanded.json (50 merchants)  
# - triggers_expanded.json (100 triggers)
# - categories/ folder with 5 category JSON files
```
- [ ] All 4 data files present
- [ ] Files are valid JSON (no corruption)
- [ ] Dataset loading works in bot startup

### ✅ Phase 4: Local Stress Test (Optional)
```bash
# Load all contexts
for context in dataset/expanded/categories/*.json; do
  echo "Loading $context"
done

# Simulate 10 tick operations
# Simulate 5 reply operations
# Check that suppression keys work (no duplicate sends)
```
- [ ] No memory leaks (uptime_seconds stable)
- [ ] No duplicate messages (suppression works)
- [ ] Conversation state tracking works
- [ ] Performance acceptable (<100ms per request)

---

## Replit Deployment Steps

### Step 1: Prepare GitHub Repository
```bash
git init
git add .
git commit -m "Vera bot ready for deployment"
git push origin main
```
- [ ] All files committed
- [ ] .gitignore includes __pycache__, *.pyc, .env (but not .env.example)
- [ ] README.md has clear instructions

### Step 2: Replit Import
1. Go to https://replit.com/new
2. Click "Import from GitHub"
3. Enter your GitHub repo URL
4. Replit auto-detects Python and creates environment
5. `.replit` file auto-configures Flask to run on port 5000

- [ ] Replit recognizes `.replit` config
- [ ] Python 3.11 environment created
- [ ] Dependencies installed from requirements.txt
- [ ] Bot starts automatically (or run button works)

### Step 3: Replit Testing
1. Click "Run" button
2. Check console for "Running on http://0.0.0.0:5000"
3. Open "Webview" tab to test endpoints

```bash
# In Replit shell, test endpoints:
curl https://<your-replit-url>/v1/healthz
curl https://<your-replit-url>/v1/metadata
```

- [ ] Bot runs without errors on Replit
- [ ] Endpoints respond correctly
- [ ] Webview shows responses
- [ ] Console shows no warnings/errors

### Step 4: Generate Replit Share URL
1. Click "Share" button (top-right)
2. Copy public URL
3. Your bot is now live!

- [ ] Public URL is accessible
- [ ] Endpoints respond from public URL
- [ ] CORS/auth not blocking requests

---

## Judge Submission Checklist

### ✅ What to Submit

**Endpoint URL** (from Replit share):
```
https://<your-replit>.replit.dev
```

**5 Required Endpoints**:
- [ ] `GET /v1/healthz` — Health check
- [ ] `GET /v1/metadata` — Bot metadata
- [ ] `POST /v1/context` — Context acceptance
- [ ] `POST /v1/tick` — Message decision
- [ ] `POST /v1/reply` — Reply handling

**Submission Form Fields**:
- [ ] **Team Name**: Vera Bot Challenge Team
- [ ] **Endpoint URL**: https://<your-replit>.replit.dev
- [ ] **Framework**: Flask 3.0.0
- [ ] **Language**: Python 3.11
- [ ] **Model Used**: claude-3-5-sonnet-20241022
- [ ] **Approach**: Multi-context composer with trigger-kind dispatch
- [ ] **Live Endpoints**: 5 (healthz, metadata, context, tick, reply)

### ✅ Judge Simulation (Before Submitting)

Run `judge_simulator.py` to test your bot:
```bash
python3 judge_simulator.py
```

Expected output:
```
Loading bot endpoint: https://<your-replit>.replit.dev
Testing /v1/healthz... ✓
Testing /v1/metadata... ✓
Testing /v1/context (category)... ✓
Testing /v1/context (merchant)... ✓
Testing /v1/context (customer)... ✓
Testing /v1/context (trigger)... ✓
Testing /v1/tick with triggers... ✓
Testing /v1/reply (affirmative)... ✓
Testing /v1/reply (opt-out)... ✓
All tests passed: 13/13 ✓
```

- [ ] All judge simulation tests pass
- [ ] No timeouts or errors
- [ ] Response times under 2 seconds each
- [ ] Bot handles 50+ concurrent context loads

---

## Troubleshooting Guide

### Bot Won't Start on Replit
**Problem**: "ModuleNotFoundError: No module named 'flask'"
**Solution**:
1. Click "Packages" → Search for "flask"
2. Or manually run: `pip install -r requirements.txt`
3. Restart bot

### Endpoints Return 500 Error
**Problem**: "Internal Server Error"
**Solution**:
1. Check Replit console for error trace
2. Ensure JSON is valid in POST requests
3. Verify all required fields present
4. Check for typos in endpoint URLs

### Hardcoded Port Issues
**Problem**: "Port 5000 already in use"
**Solution**: 
- Replit auto-assigns random port
- Bot uses `os.environ.get("PORT", 5000)` correctly
- No manual port changes needed

### Timezone/DateTime Issues
**Problem**: "datetime.utcnow() deprecated"
**Solution**:
- ✅ Already fixed in hardened version
- All calls use `datetime.now(timezone.utc)`

### JSON Parsing Errors
**Problem**: "error": "Invalid JSON"
**Solution**:
- Ensure request body is valid JSON
- Include `"Content-Type: application/json"` header
- No trailing commas in JSON objects

---

## Final Submission Template

```markdown
# Vera Bot - Merchant WhatsApp Assistant

## Endpoint
https://<your-replit>.replit.dev

## Implementation Summary
- **Framework**: Flask 3.0.0 (Python 3.11)
- **Approach**: Multi-context composer with 4-context framework
- **Key Features**:
  - Category, Merchant, Customer, Trigger context handling
  - Trigger-kind based message dispatch (research_digest, perf_spike, recall_due, dormant_with_vera)
  - Suppression key deduplication
  - Conversation state tracking with auto-reply backoff
  - Intelligent reply handling (yes/no, opt-out, question detection, out-of-scope)
  - Version-based idempotency (409 on stale)

## 5 Live Endpoints
1. `GET /v1/healthz` - Health check with uptime and context counts
2. `GET /v1/metadata` - Bot metadata and team info
3. `POST /v1/context` - Receive category/merchant/customer/trigger context
4. `POST /v1/tick` - Compose messages for available triggers
5. `POST /v1/reply` - Handle merchant replies and decide actions

## Test Results
✓ All 5 endpoints live and responding
✓ 13/13 local test scenarios passing
✓ Dataset: 50 merchants, 200 customers, 100 triggers, 5 categories
✓ Production hardened for Linux/Replit deployment
✓ Judge simulator: 100% pass rate

## Contact
bot@magicpin.ai
```

---

## Post-Submission (After Judge Runs Tests)

### ✅ Success Indicators
- [ ] All 5 endpoints return 200 OK responses
- [ ] Healthz shows increasing uptime
- [ ] Context acceptance returns ack_ids correctly
- [ ] Tick generates contextual messages
- [ ] Reply handling is intelligent (not generic)
- [ ] No timeout or 5xx errors
- [ ] Judge simulator reports "All tests passed"

### ✅ If Issues Arise
- [ ] Check Replit console for errors
- [ ] Review judge feedback carefully
- [ ] Fix issue locally, test, then redeploy
- [ ] Update submission URL if changed
- [ ] Contact challenge organizers with debug logs

---

**Submission Ready**: When all ✓ boxes are checked, you're ready to submit!
