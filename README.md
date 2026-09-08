# Vera Bot

**Deterministic merchant-engagement assistant backend for WhatsApp-oriented workflows.**

Vera Bot accepts category, merchant, customer, and trigger context, then composes context-aware actions while managing conversation state, suppression, de-duplication, and reply handling.

## What It Does

- Accepts versioned context through REST endpoints
- Composes messages for supported trigger types
- Tailors messages using category and merchant context
- Detects auto-replies, opt-outs, questions, and affirmative engagement
- Tracks conversation state and suppression keys
- Returns structured JSON responses for API consumers

## API

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/v1/healthz` | GET | Health and loaded-context status |
| `/v1/metadata` | GET | Bot metadata and version information |
| `/v1/context` | POST | Store versioned category/merchant/customer/trigger context |
| `/v1/tick` | POST | Compose actions from available triggers |
| `/v1/reply` | POST | Process incoming merchant/customer replies |

## Architecture

```text
Context APIs
    |
    v
   BotState
    |
    +--> version validation
    +--> conversation state
    +--> suppression / de-duplication
    |
    v
MessageComposer
    |
    +--> trigger dispatch
    +--> category context
    +--> merchant context
    +--> customer context
    |
    v
Structured API action
```

## Key Engineering Details

### Versioned state

Contexts are stored with versions. Older versions are rejected as stale, preventing outdated context from replacing newer data.

### Trigger-aware composition

The composer dispatches behavior by trigger kind, including research digests, performance spikes, recall reminders, and dormant-merchant re-engagement.

### Conversation safeguards

The implementation tracks ended conversations and suppression keys so that duplicate or inappropriate follow-up actions can be skipped.

### Reply handling

Incoming replies are classified for cases such as auto-replies, opt-outs, affirmative responses, questions, and out-of-scope messages.

## Technology Stack

- **Language:** Python 3.11+
- **Framework:** Flask
- **API style:** JSON REST endpoints
- **Configuration:** Environment variables
- **Deployment support:** Procfile / cloud-friendly Python deployment

## Repository Structure

```text
vera-bot/
├── bot.py
├── requirements.txt
├── Procfile
├── dataset/
├── examples/
├── QUICK_START.md
├── DEPLOYMENT.md
├── TEST_RESULTS.md
├── IMPLEMENTATION_SUMMARY.md
└── README.md
```

## Run Locally

```bash
pip install -r requirements.txt
python bot.py
```

The API listens on the application port configured by the project. Test the health endpoint with:

```bash
curl http://localhost:8080/v1/healthz
```

## Testing

The repository includes a documented test suite covering the five API endpoints, version handling, message composition, auto-reply detection, and opt-out behavior. See `TEST_RESULTS.md` for the project-specific test scenarios and results.

## Dataset

The repository includes deterministic challenge data covering five merchant categories, merchant/customer contexts, triggers, and test pairs. The dataset supports repeatable local evaluation of the message-composition workflow.

## Important Implementation Note

The repository implements a deterministic message-composition backend. The README intentionally does not claim a specific external foundation model as the runtime engine because the repository documentation previously referenced different model names. The current implementation should be treated as the source of truth for any model integration details.

## Author

**Harsh Shrivastava**  
[GitHub](https://github.com/Harsh24-j) · [LinkedIn](https://linkedin.com/in/harshshrivastava24)
