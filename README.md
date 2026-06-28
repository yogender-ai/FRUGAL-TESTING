# Frugal Testing Section A Harness

FastAPI + Playwright implementation for the AI-Native Software Engineer Intern practical section.

## What This Project Covers

- **Canvas/WebSocket automation:** FastAPI serves a live HTML5 Canvas telemetry board over WebSockets. Playwright intercepts the WebSocket stream, applies Fibonacci jitter, corrupts a server frame, scans canvas pixels with `requestAnimationFrame`, and executes a hover -> drag -> click chain through a circuit-breaker coordinate macro.
- **Replay-protected API:** FastAPI exposes a local transaction API with nonce, server timestamp, salt sequence, and `X-Frugal-Mac` HMAC-SHA512 validation. Playwright API tests resend an identical packet within 150 ms and assert replay rejection.
- **Shadow DOM/accessibility artifact:** FastAPI serves a nested Shadow DOM page and the repo includes a strict accessibility-tree prompt artifact.
- **Runner dashboard:** Stitch-generated dashboard served by FastAPI at `/dashboard`, connected to controlled Playwright modules and JSON report export.
- **Cloud Command smoke:** Optional Playwright test for the deployed Cloud Command backend and, when configured, frontend.

## Run

```powershell
cd "A:\projects\frugal testing"
python -m pytest -q
```

Run the dashboard:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Open:

```text
http://127.0.0.1:8010/dashboard
```

Optional deployed Cloud Command smoke:

```powershell
$env:RUN_CLOUD_COMMAND_SMOKE="1"
python -m pytest tests/test_cloud_command_smoke.py -q
```

Defaults and overrides:

- Backend: `https://cloud-command.onrender.com`
- Frontend: no default because the old `cloud-command.vercel.app` deployment returns Vercel 404. Set `CLOUD_COMMAND_URL` to the current frontend URL before running the frontend smoke.

Override if your deployment URL changes:

```powershell
$env:CLOUD_COMMAND_URL="https://your-frontend.vercel.app"
$env:CLOUD_COMMAND_API_URL="https://your-backend.onrender.com"
```

## Video Walkthrough Checklist

For each practical Google Drive folder, record:

1. The terminal output from `python -m pytest -q`.
2. The source code files in this folder.
3. The GenAI prompt/history window used while building and debugging.
