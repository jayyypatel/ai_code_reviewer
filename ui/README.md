# AI Code Reviewer UI

React + Vite frontend for the Django REST backend.

## Features

- Submit raw code to `/review/`
- Submit GitHub repo + PR number to `/github-review/`
- Optionally post PR comments via `/github-comment/`
- Render structured review findings with severity badges

## Run locally

1. Start backend on `http://127.0.0.1:8000`
2. Start UI:

```bash
cd ui
npm install
npm run dev
```

Vite runs on `http://127.0.0.1:5173` and proxies API requests to the backend.

## Build

```bash
npm run build
npm run preview
```
