# Shelby - AI Code Review Agent

Production-oriented Django + React system that reviews GitHub Pull Requests with AI, returns structured findings, and stores full review runs for traceability.

---

## What This Project Does

- Accepts a GitHub PR URL (or `repo` + `pull_number`) from UI/API.
- Fetches PR changed files/diff from GitHub API.
- Parses reviewable changed lines.
- Builds a high-signal review prompt (static policy + optional user context).
- Sends prompt to Gemini (`google-genai`) and normalizes results.
- Returns structured findings to the UI.
- Persists each review run (prompt, diff payload, raw AI output, normalized findings, status, duration).

---

## Core Stack

- Python 3.11+ / Django 6 / Django REST Framework
- Requests (GitHub API)
- Google Gemini via `google-genai`
- SQLite (default) for persistence
- React + Vite frontend in `ui/`

---

## Architecture

Business logic is isolated in services; views are thin orchestration layers.

```text
backend/
├── ai_code_reviewer/
│   ├── settings.py
│   └── urls.py
├── reviewer/
│   ├── models.py                 # ReviewRun persistence model
│   ├── serializers.py            # request validation + URL parsing
│   ├── views.py                  # API views only (no heavy business logic)
│   ├── urls.py                   # reviewer endpoints
│   ├── services/
│   │   ├── ai_service.py         # Gemini call + retry + JSON recovery
│   │   ├── github_service.py     # GitHub API calls
│   │   ├── review_engine.py      # prompt build + normalization + DB logging
│   │   └── exceptions.py
│   └── utils/
│       └── diff_parser.py        # changed-line extraction
└── ui/                           # premium Shelby frontend
```

---

## API Endpoints

### `POST /github-review/`

Primary review endpoint.

**Input (recommended):**

```json
{
  "pr_url": "https://github.com/owner/repo/pull/123",
  "user_context": "Focus on security and backward compatibility."
}
```

**Input (fallback):**

```json
{
  "repo": "owner/repo",
  "pull_number": 123,
  "user_context": "Optional context"
}
```

**Response (strict findings schema):**

```json
[
  {
    "type": "bug | performance | security | improvement",
    "severity": "low | medium | high",
    "file": "string",
    "line": 42,
    "title": "string",
    "explanation": "string",
    "suggestion": "string",
    "fixed_code": "string or null"
  }
]
```

---

### `GET /review-runs/`

Returns the latest 20 persisted review runs for audit/debug.

Useful to inspect:

- extracted repo + PR
- user context
- changed lines payload passed to prompt
- final prompt text
- raw AI output
- normalized findings
- status/error/duration

---

### `POST /github-comment/`

Optional endpoint for posting comments back to GitHub PRs.

---

## Data Model

`ReviewRun` stores end-to-end review telemetry.

Key fields:

- `repo`, `pull_number`, `pr_url`
- `user_context`
- `changed_lines_payload` (JSON)
- `prompt_sent` (text)
- `raw_ai_output` (JSON)
- `normalized_findings` (JSON)
- `status` (`success` / `failed`)
- `error_message`
- `duration_ms`
- `created_at`

---

## Environment Configuration

Create `backend/.env` (or copy from `.env.example`):

```env
DJANGO_SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.0-flash-lite
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta
GEMINI_TIMEOUT_SECONDS=30
GEMINI_MAX_RETRIES=2
GEMINI_RETRY_BACKOFF_SECONDS=1.5

GITHUB_TOKEN=ghp_xxx
GITHUB_API_BASE_URL=https://api.github.com
GITHUB_TIMEOUT_SECONDS=20

LOG_LEVEL=INFO
```

### Important

- `GITHUB_TOKEN` is strongly recommended (avoids anonymous rate-limit 403).
- Restart Django after `.env` changes.

---

## Run Locally

### Backend

```bash
cd backend
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py runserver 127.0.0.1:8000
```

### Frontend

```bash
cd backend/ui
npm install
npm run dev
```

Frontend runs on `http://127.0.0.1:5173` and proxies API calls to backend on `http://127.0.0.1:8000`.

---

## Prompting Strategy

Prompt generation lives in `reviewer/services/review_engine.py`:

- static policy (high-signal, severity calibration, strict schema)
- dynamic context from user input (`user_context`)
- diff payload from parsed changed lines

This enables consistent guardrails plus per-request intent control.

---

## Reliability Notes

- Gemini transient failures (`429/500/502/503/504`) are retried with exponential backoff.
- JSON output parser recovers from common model wrapping (fenced JSON / extra prose).
- Validation catches invalid PR URL format before API execution.

---

## UI Summary

The `ui/` app provides:

- premium dark visual design
- PR URL + optional review context input
- animated loading state + elapsed timer
- toast feedback and findings accordion

Only essential review workflow is included (no extra dashboard clutter).

---

## Admin & Debugging

- `ReviewRun` is registered in Django admin for quick inspection.
- Use `/review-runs/` for API-level inspection in local/dev tools.

---

## Common Errors

- **GitHub 403 rate limit**: set `GITHUB_TOKEN` and restart server.
- **Gemini quota/availability errors**: switch to lower-cost model and verify project quota.
- **Import mismatch**: run Django with project venv explicitly (`./.venv/bin/python ...`).
