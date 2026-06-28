import asyncio
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Set, Tuple

from fastapi import FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel

from app.constants import CANVAS_STREAM_HTML, SHADOW_DOM_HTML


SHARED_SECRET = os.getenv("FRUGAL_SHARED_SECRET", "frugal-testing-local-secret").encode("utf-8")


@dataclass
class TransactionState:
    nonce: str
    server_timestamp_us: str
    salt_sequence: str
    seen_packets: Set[Tuple[str, str]] = field(default_factory=set)


transactions: Dict[str, TransactionState] = {}


class RunRequest(BaseModel):
    target_url: str = ""
    modules: list[str]


app = FastAPI(
    title="Frugal Testing Automation Harness",
    description="Local Canvas/WebSocket and replay-security testbed for Section A.",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "frugal-section-a-harness"}


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)


@app.get("/", response_class=HTMLResponse)
def dashboard_home():
    return dashboard()


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    dashboard_path = Path(__file__).resolve().parents[1] / "frontend" / "code.html"
    return HTMLResponse(dashboard_path.read_text(encoding="utf-8"))


@app.get("/api/runner/modules")
def runner_modules():
    return {
        "modules": [
            {"id": "smoke", "label": "Smoke Test", "needs_target": True},
            {"id": "visual", "label": "Visual Blank Screen Detection", "needs_target": True},
            {"id": "console", "label": "Console Error Scan", "needs_target": True},
            {"id": "network", "label": "Network Failure Audit", "needs_target": True},
            {"id": "q1_canvas", "label": "Canvas/WebSocket Race Test", "needs_target": False},
            {"id": "q2_replay", "label": "HMAC Replay Security Test", "needs_target": False},
            {"id": "q3_shadow", "label": "Shadow DOM Accessibility Test", "needs_target": False},
            {"id": "cloud_backend", "label": "Cloud Command Backend Health", "needs_target": False},
        ]
    }


@app.post("/api/runner/runs")
def start_runner_run(payload: RunRequest, request: Request):
    from app.runner import create_run

    allowed = {
        "smoke",
        "visual",
        "console",
        "network",
        "q1_canvas",
        "q2_replay",
        "q3_shadow",
        "cloud_backend",
    }
    modules = [module for module in payload.modules if module in allowed]
    if not modules:
        raise HTTPException(status_code=400, detail="Select at least one supported test module")
    base_url = str(request.base_url).rstrip("/")
    return create_run(payload.target_url.strip(), modules, base_url)


@app.get("/api/runner/runs")
def get_runner_runs():
    from app.runner import list_runs

    return {"runs": list_runs()}


@app.get("/api/runner/runs/{run_id}")
def get_runner_run(run_id: str):
    from app.runner import get_run

    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/q1", response_class=HTMLResponse)
def q1_canvas_testbed():
    return HTMLResponse(CANVAS_STREAM_HTML)


@app.websocket("/ws/telemetry")
async def telemetry_socket(websocket: WebSocket):
    await websocket.accept()
    frames = [
        {"seq": 1, "status": "loading", "x": 90, "y": 90, "color": "#9ca3af", "balance": 1000},
        {"seq": 2, "status": "loading", "x": 170, "y": 115, "color": "#9ca3af", "balance": 1004},
        {"seq": 3, "status": "active", "x": 260, "y": 150, "color": "#22c55e", "balance": 1022},
        {"seq": 4, "status": "active", "x": 330, "y": 180, "color": "#38bdf8", "balance": 1030},
        {"seq": 5, "status": "active", "x": 410, "y": 220, "color": "#a78bfa", "balance": 1042},
    ]
    try:
        for frame in frames:
            await websocket.send_text(json.dumps(frame))
            await asyncio.sleep(0.08)
        await websocket.close(code=1000)
    except WebSocketDisconnect:
        return


@app.post("/api/q2/reset")
def reset_transactions():
    transactions.clear()
    return {"status": "reset"}


@app.post("/api/q2/transactions")
async def create_transaction(request: Request):
    await request.body()
    tx_id = f"txn_{secrets.token_hex(8)}"
    nonce = secrets.token_hex(16)
    timestamp_us = str(time.time_ns() // 1000)
    salt_sequence = secrets.token_hex(8)
    transactions[tx_id] = TransactionState(
        nonce=nonce,
        server_timestamp_us=timestamp_us,
        salt_sequence=salt_sequence,
    )
    return JSONResponse(
        {"transaction_id": tx_id, "status": "created"},
        status_code=201,
        headers={
            "X-Transaction-Id": tx_id,
            "X-Frugal-Nonce": nonce,
            "X-Server-Timestamp-Us": timestamp_us,
            "X-Salt-Sequence": salt_sequence,
        },
    )


@app.put("/api/q2/transactions/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    request: Request,
    x_frugal_mac: str = Header(...),
    x_frugal_timestamp_us: str = Header(...),
    x_frugal_nonce: str = Header(...),
    x_salt_sequence: str = Header(...),
):
    state = transactions.get(transaction_id)
    if not state:
        raise HTTPException(status_code=404, detail="Unknown transaction")

    raw_body = await request.body()
    if x_frugal_nonce != state.nonce or x_salt_sequence != state.salt_sequence:
        raise HTTPException(status_code=401, detail="Invalid nonce or salt sequence")

    expected = build_mac(raw_body, x_frugal_timestamp_us, x_salt_sequence, x_frugal_nonce)
    if not hmac.compare_digest(expected, x_frugal_mac):
        raise HTTPException(status_code=401, detail="Invalid X-Frugal-Mac")

    replay_key = (x_frugal_timestamp_us, x_frugal_mac)
    if replay_key in state.seen_packets:
        return JSONResponse(
            {
                "status": "rejected",
                "reason": "replay_detected",
                "alert": "HIGH_RISK_DATA_MUTATION_REPLAY_ATTEMPT",
            },
            status_code=409,
        )

    state.seen_packets.add(replay_key)
    return {
        "transaction_id": transaction_id,
        "status": "updated",
        "validated_by": "hmac-sha512",
    }


@app.get("/q3", response_class=HTMLResponse)
def q3_shadow_dom_testbed():
    return HTMLResponse(SHADOW_DOM_HTML)


def build_mac(raw_body: bytes, timestamp_us: str, salt_sequence: str, nonce: str) -> str:
    material = b".".join(
        [
            raw_body,
            timestamp_us.encode("utf-8"),
            salt_sequence.encode("utf-8"),
            nonce.encode("utf-8"),
        ]
    )
    return hmac.new(SHARED_SECRET, material, hashlib.sha512).hexdigest()


