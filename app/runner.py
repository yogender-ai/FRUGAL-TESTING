import hashlib
import hmac
import json
import re
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

import httpx
from playwright.sync_api import sync_playwright

from app.main import SHARED_SECRET


RUNS: Dict[str, dict] = {}
RUN_LOCK = threading.Lock()


def create_run(target_url: str, modules: List[str], base_url: str) -> dict:
    run_id = uuid.uuid4().hex[:12]
    run = {
        "id": run_id,
        "target_url": target_url,
        "modules": modules,
        "status": "queued",
        "score": 0,
        "risk": "Unknown",
        "passed": 0,
        "failed": 0,
        "avg_response_ms": 0,
        "logs": [],
        "findings": [],
        "started_at": datetime.utcnow().isoformat() + "Z",
        "completed_at": None,
    }
    with RUN_LOCK:
        RUNS[run_id] = run

    thread = threading.Thread(target=_run_suite, args=(run_id, target_url, modules, base_url), daemon=True)
    thread.start()
    return run


def get_run(run_id: str) -> dict | None:
    with RUN_LOCK:
        run = RUNS.get(run_id)
        return dict(run) if run else None


def list_runs() -> List[dict]:
    with RUN_LOCK:
        return list(reversed([dict(run) for run in RUNS.values()]))


def _log(run_id: str, level: str, message: str):
    with RUN_LOCK:
        run = RUNS[run_id]
        run["logs"].append(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "level": level,
                "message": message,
            }
        )


def _finding(run_id: str, status: str, module: str, message: str, detail: str = ""):
    with RUN_LOCK:
        RUNS[run_id]["findings"].append(
            {
                "status": status,
                "module": module,
                "message": message,
                "detail": detail,
            }
        )


def _set_status(run_id: str, status: str):
    with RUN_LOCK:
        RUNS[run_id]["status"] = status


def _finish(run_id: str, durations: List[float]):
    with RUN_LOCK:
        run = RUNS[run_id]
        passed = sum(1 for item in run["findings"] if item["status"] == "passed")
        failed = sum(1 for item in run["findings"] if item["status"] == "failed")
        total = max(passed + failed, 1)
        score = round((passed / total) * 100)
        run["passed"] = passed
        run["failed"] = failed
        run["score"] = score
        run["risk"] = "Low" if score >= 85 else "Medium" if score >= 65 else "High"
        run["avg_response_ms"] = round(sum(durations) / len(durations)) if durations else 0
        run["status"] = "passed" if failed == 0 else "failed"
        run["completed_at"] = datetime.utcnow().isoformat() + "Z"


def _run_suite(run_id: str, target_url: str, modules: List[str], base_url: str):
    durations = []
    try:
        _set_status(run_id, "running")
        _log(run_id, "SYSTEM", "Run accepted by FastAPI orchestration layer.")
        _log(run_id, "INFO", f"Target: {target_url or 'local harness'}")
        _log(run_id, "INFO", f"Modules: {', '.join(modules)}")

        if "smoke" in modules:
            durations.append(_module_smoke(run_id, target_url))
        if "visual" in modules:
            durations.append(_module_visual(run_id, target_url))
        if "console" in modules:
            durations.append(_module_console(run_id, target_url))
        if "network" in modules:
            durations.append(_module_network(run_id, target_url))
        if "q1_canvas" in modules:
            durations.append(_module_q1_canvas(run_id, base_url))
        if "q2_replay" in modules:
            durations.append(_module_q2_replay(run_id, base_url))
        if "q3_shadow" in modules:
            durations.append(_module_q3_shadow(run_id, base_url))
        if "cloud_backend" in modules:
            durations.append(_module_cloud_backend(run_id))

        _finish(run_id, durations)
        _log(run_id, "SUCCESS", "Report generated and score calculated.")
    except Exception as exc:
        _log(run_id, "ERROR", f"Runner crashed: {exc}")
        _finding(run_id, "failed", "runner", "Automation runner crashed", str(exc))
        _finish(run_id, durations)


def _valid_url(target_url: str) -> bool:
    parsed = urlparse(target_url or "")
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _launch_chromium(playwright, **kwargs):
    chrome_paths = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ]
    for path in chrome_paths:
        if path.exists():
            return playwright.chromium.launch(executable_path=str(path), **kwargs)
    return playwright.chromium.launch(**kwargs)


def _module_smoke(run_id: str, target_url: str) -> float:
    started = time.perf_counter()
    if not _valid_url(target_url):
        _finding(run_id, "failed", "Smoke Test", "Target URL is missing or invalid")
        return 0
    _log(run_id, "SYSTEM", "Starting browser smoke test.")
    with sync_playwright() as p:
        browser = _launch_chromium(p)
        page = browser.new_page()
        response = page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
        title = page.title()
        body_len = page.locator("body").evaluate("body => body.innerText.trim().length")
        ok = bool(response and response.status < 400 and title and body_len > 20)
        if ok:
            _finding(run_id, "passed", "Smoke Test", "Page loaded with visible body content", title)
            _log(run_id, "SUCCESS", f"Smoke passed with title: {title}")
        else:
            _finding(run_id, "failed", "Smoke Test", "Page failed basic load/content checks", f"title={title}, body_len={body_len}")
        browser.close()
    return (time.perf_counter() - started) * 1000


def _module_visual(run_id: str, target_url: str) -> float:
    started = time.perf_counter()
    if not _valid_url(target_url):
        _finding(run_id, "failed", "Visual Blank Screen", "Target URL is missing or invalid")
        return 0
    _log(run_id, "SYSTEM", "Checking for blank-screen rendering failure.")
    with sync_playwright() as p:
        browser = _launch_chromium(p)
        page = browser.new_page(viewport={"width": 1366, "height": 768})
        page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
        visible_text = page.locator("body").evaluate("body => body.innerText.trim().length")
        box_count = page.locator("body *").evaluate_all("nodes => nodes.filter(n => n.getBoundingClientRect().width > 0 && n.getBoundingClientRect().height > 0).length")
        if visible_text > 20 and box_count > 3:
            _finding(run_id, "passed", "Visual Blank Screen", "Rendered content is non-empty", f"text={visible_text}, boxes={box_count}")
            _log(run_id, "SUCCESS", "Visual health check passed.")
        else:
            _finding(run_id, "failed", "Visual Blank Screen", "Possible blank screen detected", f"text={visible_text}, boxes={box_count}")
        browser.close()
    return (time.perf_counter() - started) * 1000


def _module_console(run_id: str, target_url: str) -> float:
    started = time.perf_counter()
    if not _valid_url(target_url):
        _finding(run_id, "failed", "Console Scan", "Target URL is missing or invalid")
        return 0
    errors = []
    _log(run_id, "SYSTEM", "Collecting browser console errors.")
    with sync_playwright() as p:
        browser = _launch_chromium(p)
        page = browser.new_page()
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(1500)
        if errors:
            _finding(run_id, "failed", "Console Scan", "Console errors were emitted", " | ".join(errors[:3]))
            _log(run_id, "WARN", f"Console scan found {len(errors)} error(s).")
        else:
            _finding(run_id, "passed", "Console Scan", "No browser console errors found")
            _log(run_id, "SUCCESS", "Console scan passed.")
        browser.close()
    return (time.perf_counter() - started) * 1000


def _module_network(run_id: str, target_url: str) -> float:
    started = time.perf_counter()
    if not _valid_url(target_url):
        _finding(run_id, "failed", "Network Audit", "Target URL is missing or invalid")
        return 0
    failures = []
    slow = []
    timestamps = {}
    _log(run_id, "SYSTEM", "Auditing failed and slow network requests.")
    with sync_playwright() as p:
        browser = _launch_chromium(p)
        page = browser.new_page()
        page.on("request", lambda req: timestamps.setdefault(req, time.perf_counter()))
        page.on("requestfailed", lambda req: failures.append(req.url))

        def on_finished(req):
            elapsed = (time.perf_counter() - timestamps.get(req, time.perf_counter())) * 1000
            if elapsed > 3000:
                slow.append((req.url, round(elapsed)))

        page.on("requestfinished", on_finished)
        page.goto(target_url, wait_until="networkidle", timeout=45000)
        if failures:
            _finding(run_id, "failed", "Network Audit", "Failed network requests detected", failures[0])
        else:
            detail = f"{len(slow)} slow request(s)" if slow else "No failed requests"
            _finding(run_id, "passed", "Network Audit", "Network audit completed", detail)
        _log(run_id, "SUCCESS" if not failures else "WARN", f"Network audit finished: failures={len(failures)}, slow={len(slow)}")
        browser.close()
    return (time.perf_counter() - started) * 1000


def _module_q1_canvas(run_id: str, base_url: str) -> float:
    started = time.perf_counter()
    _log(run_id, "SYSTEM", "Running Canvas/WebSocket race interception.")
    with sync_playwright() as p:
        browser = _launch_chromium(p)
        page = browser.new_page(viewport={"width": 1100, "height": 760})
        jitter_log = []

        def route_socket(ws):
            server = ws.connect_to_server()
            fib = [1, 1, 2, 3, 5, 8]
            state = {"index": 0}

            def on_server_message(message):
                frame = json.loads(message)
                delay_ms = min(1000 * fib[min(state["index"], len(fib) - 1)], 8000)
                state["index"] += 1
                if frame["seq"] == 5:
                    frame["balance"] = "1e+7"
                jitter_log.append({"seq": frame["seq"], "delay_ms": delay_ms})
                time.sleep(delay_ms / 1000)
                ws.send(json.dumps(frame))

            server.on_message(on_server_message)
            ws.on_message(lambda message: server.send(message))

        page.route_web_socket("**/ws/telemetry", route_socket)
        page.goto(f"{base_url}/q1")
        page.wait_for_function("() => window.__canvasMetrics?.status === 'active' && window.__canvasMetrics?.target", timeout=9000)
        action = page.evaluate("() => window.__coordinateCircuitBreaker()")
        page.locator('[data-testid="exception-boundary"]').wait_for(timeout=9000)
        if 30 <= action["durationMs"] <= 100 and any(item["seq"] == 5 for item in jitter_log):
            _finding(run_id, "passed", "Canvas/WebSocket", "Jitter, corruption, pixel scan, and circuit-breaker action passed")
            _log(run_id, "SUCCESS", "Canvas/WebSocket automation passed.")
        else:
            _finding(run_id, "failed", "Canvas/WebSocket", "Canvas timing or corruption assertion failed", str(action))
        browser.close()
    return (time.perf_counter() - started) * 1000


def _module_q2_replay(run_id: str, base_url: str) -> float:
    started = time.perf_counter()
    _log(run_id, "SYSTEM", "Running HMAC replay security test.")
    with httpx.Client(base_url=base_url, timeout=20.0) as client:
        client.post("/api/q2/reset")
        create = client.post("/api/q2/transactions", json={"amount": 1900, "currency": "INR"})
        tx_id = create.headers["x-transaction-id"]
        nonce = create.headers["x-frugal-nonce"]
        salt = create.headers["x-salt-sequence"]
        timestamp_us = create.headers["x-server-timestamp-us"]
        raw_body = json.dumps({"amount": 2150, "currency": "INR", "risk_model": "replay-boundary"}, separators=(",", ":"))
        mac = _build_mac(raw_body, timestamp_us, salt, nonce)
        headers = {
            "Content-Type": "application/json",
            "X-Frugal-Nonce": nonce,
            "X-Frugal-Timestamp-Us": timestamp_us,
            "X-Salt-Sequence": salt,
            "X-Frugal-Mac": mac,
        }
        first = client.put(f"/api/q2/transactions/{tx_id}", content=raw_body, headers=headers)
        replay_started = time.perf_counter()
        replay = client.put(f"/api/q2/transactions/{tx_id}", content=raw_body, headers=headers)
        elapsed_ms = (time.perf_counter() - replay_started) * 1000
        if first.status_code == 200 and replay.status_code == 409 and elapsed_ms < 150:
            _finding(run_id, "passed", "HMAC Replay", "Replay attack rejected within 150 ms", f"{round(elapsed_ms, 2)} ms")
            _log(run_id, "SUCCESS", "Replay security boundary passed.")
        else:
            _finding(run_id, "failed", "HMAC Replay", "Replay boundary failed", f"first={first.status_code}, replay={replay.status_code}, ms={elapsed_ms}")
    return (time.perf_counter() - started) * 1000


def _module_q3_shadow(run_id: str, base_url: str) -> float:
    started = time.perf_counter()
    _log(run_id, "SYSTEM", "Running Shadow DOM accessibility-tree validation.")
    with sync_playwright() as p:
        browser = _launch_chromium(p)
        page = browser.new_page()
        page.goto(f"{base_url}/q3")
        button = page.get_by_role("button", name=re.compile("Approve isolated replay", re.I))
        button.click()
        snapshot = page.accessibility.snapshot(interesting_only=False)
        if "Approve isolated replay protection transfer" in str(snapshot):
            _finding(run_id, "passed", "Shadow DOM", "Target resolved through role/accessibility metadata")
            _log(run_id, "SUCCESS", "Accessibility pathfinding passed.")
        else:
            _finding(run_id, "failed", "Shadow DOM", "Accessibility tree did not expose expected control")
        browser.close()
    return (time.perf_counter() - started) * 1000


def _module_cloud_backend(run_id: str) -> float:
    started = time.perf_counter()
    url = "https://cloud-command.onrender.com/api/keep-alive"
    _log(run_id, "SYSTEM", "Checking deployed Cloud Command backend.")
    with httpx.Client(timeout=45.0) as client:
        response = client.get(url)
        if response.status_code == 200 and response.json().get("service") == "cloud-command":
            _finding(run_id, "passed", "Cloud Command Backend", "Deployed backend keep-alive passed", url)
            _log(run_id, "SUCCESS", "Cloud Command backend is alive.")
        else:
            _finding(run_id, "failed", "Cloud Command Backend", "Backend health check failed", f"{response.status_code}")
    return (time.perf_counter() - started) * 1000


def _build_mac(raw_body: str, timestamp_us: str, salt_sequence: str, nonce: str) -> str:
    material = b".".join(
        [
            raw_body.encode("utf-8"),
            timestamp_us.encode("utf-8"),
            salt_sequence.encode("utf-8"),
            nonce.encode("utf-8"),
        ]
    )
    return hmac.new(SHARED_SECRET, material, hashlib.sha512).hexdigest()
