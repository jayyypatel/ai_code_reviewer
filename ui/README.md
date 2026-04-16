# AI Code Reviewer UI

React + Vite frontend for the Django REST backend.

## Features

- Submit GitHub Pull Request URL to `/github-review/`
- Add optional review context passed into backend prompt
- Render structured findings with severity and expandable cards
- Premium dark Shelby-themed interface with loading timer

## Run locally

1. Start backend on `http://127.0.0.1:8000`
2. Start UI:

```bash
cd ui
npm install
npm run dev
```

Vite runs on `http://127.0.0.1:5173` and proxies API requests to the backend.

## API base URL configuration

UI supports both deployment styles:

- Same-origin backend (default): no env var required, uses relative URLs.
- Separate backend domain: set `VITE_API_BASE_URL`.

Create `ui/.env`:

```env
VITE_API_BASE_URL=https://ai-code-reviewer-ngvp.onrender.com
```

For local same-origin/proxy usage, leave it unset.

## Build

```bash
npm run build
npm run preview
```
