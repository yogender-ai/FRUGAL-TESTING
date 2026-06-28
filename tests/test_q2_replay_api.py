import hashlib
import hmac
import json
import time

from playwright.sync_api import sync_playwright

from app.main import SHARED_SECRET


def build_mac(raw_body, timestamp_us, salt_sequence, nonce):
    material = b".".join(
        [
            raw_body.encode("utf-8"),
            timestamp_us.encode("utf-8"),
            salt_sequence.encode("utf-8"),
            nonce.encode("utf-8"),
        ]
    )
    return hmac.new(SHARED_SECRET, material, hashlib.sha512).hexdigest()


def test_hmac_nonce_transaction_replay_is_rejected_within_150_ms(live_server):
    with sync_playwright() as p:
        api = p.request.new_context(base_url=live_server)
        api.post("/api/q2/reset")

        create = api.post("/api/q2/transactions", data={"amount": 1900, "currency": "INR"})
        assert create.status == 201

        tx_id = create.headers["x-transaction-id"]
        nonce = create.headers["x-frugal-nonce"]
        salt = create.headers["x-salt-sequence"]
        timestamp_us = create.headers["x-server-timestamp-us"]
        raw_body = json.dumps(
            {"amount": 2150, "currency": "INR", "risk_model": "replay-boundary"},
            separators=(",", ":"),
        )
        mac = build_mac(raw_body, timestamp_us, salt, nonce)
        headers = {
            "Content-Type": "application/json",
            "X-Frugal-Nonce": nonce,
            "X-Frugal-Timestamp-Us": timestamp_us,
            "X-Salt-Sequence": salt,
            "X-Frugal-Mac": mac,
        }

        first = api.put(f"/api/q2/transactions/{tx_id}", data=raw_body, headers=headers)
        assert first.status == 200

        replay_started = time.perf_counter()
        replay = api.put(f"/api/q2/transactions/{tx_id}", data=raw_body, headers=headers)
        replay_elapsed_ms = (time.perf_counter() - replay_started) * 1000

        assert replay_elapsed_ms < 150
        assert replay.status == 409
        assert replay.json()["alert"] == "HIGH_RISK_DATA_MUTATION_REPLAY_ATTEMPT"

        api.dispose()
