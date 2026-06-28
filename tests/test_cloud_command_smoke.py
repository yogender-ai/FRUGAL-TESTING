import os
import re

import pytest
from playwright.sync_api import expect, sync_playwright

from conftest import launch_chromium


@pytest.mark.skipif(
    os.getenv("RUN_CLOUD_COMMAND_SMOKE") != "1",
    reason="Set RUN_CLOUD_COMMAND_SMOKE=1 to test deployed Cloud Command.",
)
def test_deployed_cloud_command_backend_is_alive():
    backend_url = os.getenv("CLOUD_COMMAND_API_URL", "https://cloud-command.onrender.com")

    with sync_playwright() as p:
        api = p.request.new_context()
        health = api.get(f"{backend_url}/api/keep-alive", timeout=45000)
        assert health.status == 200
        assert health.json()["service"] == "cloud-command"
        api.dispose()


@pytest.mark.skipif(
    os.getenv("RUN_CLOUD_COMMAND_SMOKE") != "1" or not os.getenv("CLOUD_COMMAND_URL"),
    reason="Set RUN_CLOUD_COMMAND_SMOKE=1 and CLOUD_COMMAND_URL to test the deployed frontend.",
)
def test_deployed_cloud_command_frontend_is_rendering():
    frontend_url = os.environ["CLOUD_COMMAND_URL"]

    with sync_playwright() as p:
        browser = launch_chromium(p)
        page = browser.new_page()
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        page.goto(frontend_url, wait_until="networkidle", timeout=45000)
        expect(page).to_have_title(re.compile("Cloud Command", re.I))
        assert page.locator("body").evaluate("body => body.innerText.trim().length") > 30
        assert not console_errors

        browser.close()
