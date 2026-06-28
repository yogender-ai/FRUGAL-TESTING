import json
import time

from playwright.sync_api import expect, sync_playwright

from conftest import launch_chromium


def test_canvas_websocket_jitter_corruption_and_coordinate_circuit_breaker(live_server):
    with sync_playwright() as p:
        browser = launch_chromium(p)
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
        page.goto(f"{live_server}/q1")

        page.wait_for_function(
            "() => window.__canvasMetrics?.status === 'active' && window.__canvasMetrics?.target",
            timeout=9000,
        )
        action = page.evaluate("() => window.__coordinateCircuitBreaker()")

        expect(page.locator('[data-testid="exception-boundary"]')).to_be_visible(timeout=9000)
        metrics = page.evaluate("() => window.__canvasMetrics")

        assert action["durationMs"] >= 30
        assert action["durationMs"] <= 100
        assert metrics["boundaryInvoked"] is True
        assert any(entry["delay_ms"] >= 1000 for entry in jitter_log)
        assert any(entry["seq"] == 5 for entry in jitter_log)

        browser.close()
