# Vera Bot Deployment Guide

Vera Bot is a Flask API backend for deterministic, context-aware merchant engagement workflows.

## API Endpoints

- `GET /v1/healthz` — health and loaded-context counts
- `GET /v1/metadata` — bot metadata and version information
- `POST /v1/context` — store versioned category, merchant, customer, or trigger context
- `POST /v1/tick` — compose actions from available triggers
- `POST /v1/reply` — process incoming replies and decide follow-up actions

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
python bot.py
```

The application uses the `PORT` environment variable and defaults to `8080`.

Check the health endpoint:

```bash
curl http://localhost:8080/v1/healthz
```

## Production Deployment

The repository includes Gunicorn and a production-ready `Procfile`:

```text
web: gunicorn bot:app --bind 0.0.0.0:$PORT
```

A compatible Python hosting platform can use the repository directly. The platform should provide the `PORT` environment variable when required.

For a local production-style run:

```bash
gunicorn bot:app --bind 0.0.0.0:8080
```

## Configuration

The application has no required external model API key in the current deterministic implementation. Keep platform-specific credentials and secrets in deployment environment variables rather than source control.

## Testing

The repository documents endpoint-level and behavior-oriented test scenarios in `TEST_RESULTS.md`. Run the available project tests according to the repository's test files and examples.

## Production Considerations

The current implementation keeps state in process memory. A production multi-instance deployment would need durable shared state, a persistent datastore, structured observability, rate limiting, authentication/authorization, and a queue or worker model for asynchronous processing.

The application is a prototype backend; do not treat the included in-memory state as durable production storage.

## Project Structure

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

## Author

**Harsh Shrivastava**  
[GitHub](https://github.com/Harsh24-j) · [LinkedIn](https://linkedin.com/in/harshshrivastava24)
