from pathlib import Path

from playwright.sync_api import sync_playwright

from conftest import launch_chromium


def test_shadow_dom_can_be_resolved_without_static_classes_or_absolute_xpath(live_server):
    with sync_playwright() as p:
        browser = launch_chromium(p)
        page = browser.new_page()
        page.goto(f"{live_server}/q3")

        button = page.get_by_role("button", name="Approve isolated replay protection transfer")
        button.click()
        assert button.is_visible()

        snapshot = page.accessibility.snapshot(interesting_only=False)
        assert "Secure transaction control panel" in str(snapshot)
        assert "Approve isolated replay protection transfer" in str(snapshot)

        artifact = Path("artifacts/q3_accessibility_prompt.md")
        assert artifact.exists()
        assert "Do not use element IDs" in artifact.read_text(encoding="utf-8")

        browser.close()
