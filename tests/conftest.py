import socket
import threading
import time
from pathlib import Path
from urllib.request import urlopen

import pytest
import uvicorn

from app.main import app


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def launch_chromium(playwright, **kwargs):
    chrome_paths = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ]
    for path in chrome_paths:
        if path.exists():
            return playwright.chromium.launch(executable_path=str(path), **kwargs)
    return playwright.chromium.launch(**kwargs)


@pytest.fixture(scope="session")
def live_server():
    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with urlopen(f"{base_url}/health", timeout=1) as response:
                if response.status == 200:
                    break
        except Exception:
            time.sleep(0.1)
    else:
        raise RuntimeError("FastAPI test server did not start")

    yield base_url

    server.should_exit = True
    thread.join(timeout=5)
