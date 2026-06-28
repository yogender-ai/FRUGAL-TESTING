import time

import httpx


def test_runner_api_executes_assignment_modules(live_server):
    with httpx.Client(base_url=live_server, timeout=60.0) as client:
        response = client.post(
            "/api/runner/runs",
            json={
                "target_url": f"{live_server}/dashboard",
                "modules": ["q1_canvas", "q2_replay", "q3_shadow"],
            },
        )
        assert response.status_code == 200
        run_id = response.json()["id"]

        deadline = time.time() + 60
        while time.time() < deadline:
            run = client.get(f"/api/runner/runs/{run_id}").json()
            if run["status"] not in {"queued", "running"}:
                break
            time.sleep(1)
        else:
            raise AssertionError("Runner job did not finish")

        assert run["status"] == "passed"
        assert run["score"] == 100
        assert run["failed"] == 0
        assert {finding["module"] for finding in run["findings"]} == {
            "Canvas/WebSocket",
            "HMAC Replay",
            "Shadow DOM",
        }
