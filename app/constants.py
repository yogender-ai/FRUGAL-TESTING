CANVAS_STREAM_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Canvas Stream Testbed</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, system-ui, sans-serif; }
    body { margin: 0; min-height: 100vh; background: #07111f; color: #e5eefc; display: grid; place-items: center; }
    main { width: min(980px, calc(100vw - 32px)); }
    h1 { font-size: 24px; margin: 0 0 16px; }
    canvas { width: 100%; max-width: 900px; aspect-ratio: 16 / 9; border: 1px solid #1e3a5f; background: #111827; display: block; }
    [data-testid="exception-boundary"] { margin-top: 12px; padding: 12px; border: 1px solid #f97316; color: #fed7aa; background: #431407; border-radius: 6px; }
    .metric { margin-top: 10px; color: #9fb3ca; font-family: "JetBrains Mono", Consolas, monospace; }
  </style>
</head>
<body>
  <main>
    <h1>Live Mission-Control Canvas Feed</h1>
    <canvas id="stream-canvas" width="900" height="506" aria-label="Canvas telemetry grid"></canvas>
    <div class="metric" id="metric-line">Waiting for WebSocket frames...</div>
    <div id="boundary-root"></div>
  </main>
  <script>
    const canvas = document.getElementById('stream-canvas');
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const metric = document.getElementById('metric-line');
    const boundaryRoot = document.getElementById('boundary-root');
    window.__canvasMetrics = { status: 'booting', target: null, activeAt: 0, pixelSamples: [] };

    function drawGrid(frame) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#111827';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = '#25364f';
      for (let x = 0; x < canvas.width; x += 45) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
      }
      for (let y = 0; y < canvas.height; y += 45) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
      }

      ctx.fillStyle = frame.color;
      ctx.beginPath();
      ctx.roundRect(frame.x, frame.y, 92, 54, 8);
      ctx.fill();
      ctx.fillStyle = '#06101f';
      ctx.font = '700 14px Consolas';
      ctx.fillText(`SEQ ${frame.seq}`, frame.x + 16, frame.y + 32);
      metric.textContent = `seq=${frame.seq} status=${frame.status} balance=${frame.balance}`;
    }

    function scanActivePixels() {
      const width = canvas.width;
      const height = canvas.height;
      let best = null;
      for (let y = 20; y < height - 20; y += 6) {
        for (let x = 20; x < width - 20; x += 6) {
          const [r, g, b] = ctx.getImageData(x, y, 1, 1).data;
          const isGray = Math.abs(r - g) < 6 && Math.abs(g - b) < 6;
          const isBright = r + g + b > 230;
          if (isBright && !isGray) {
            best = { x, y, rgb: [r, g, b] };
            break;
          }
        }
        if (best) break;
      }
      if (best) {
        if (window.__canvasMetrics.status !== 'active') {
          window.__canvasMetrics.activeAt = performance.now();
        }
        window.__canvasMetrics.status = 'active';
        window.__canvasMetrics.target = best;
        window.__canvasMetrics.pixelSamples.push(best);
        if (window.__canvasMetrics.pixelSamples.length > 12) window.__canvasMetrics.pixelSamples.shift();
      }
      requestAnimationFrame(scanActivePixels);
    }
    requestAnimationFrame(scanActivePixels);

    function invokeBoundary(frame) {
      const unsafe = typeof frame.balance === 'string' && /e\\+|\\./i.test(frame.balance);
      if (!unsafe) return;
      boundaryRoot.innerHTML = '<div data-testid="exception-boundary">Structured exception boundary invoked: corrupted numeric state blocked.</div>';
      window.__canvasMetrics.boundaryInvoked = true;
    }

    window.__coordinateCircuitBreaker = async function coordinateCircuitBreaker() {
      const started = performance.now();
      for (let attempt = 0; attempt < 4; attempt++) {
        const target = window.__canvasMetrics.target;
        if (!target) await new Promise(resolve => requestAnimationFrame(resolve));
        const fresh = window.__canvasMetrics.target;
        if (!fresh) continue;
        const rect = canvas.getBoundingClientRect();
        const scaleX = rect.width / canvas.width;
        const scaleY = rect.height / canvas.height;
        const clientX = rect.left + fresh.x * scaleX;
        const clientY = rect.top + fresh.y * scaleY;
        const eventInit = { bubbles: true, cancelable: true, clientX, clientY };
        canvas.dispatchEvent(new MouseEvent('mousemove', eventInit));
        canvas.dispatchEvent(new MouseEvent('mousedown', eventInit));
        canvas.dispatchEvent(new MouseEvent('mousemove', { ...eventInit, clientX: clientX + 15 }));
        canvas.dispatchEvent(new MouseEvent('mouseup', { ...eventInit, clientX: clientX + 15 }));
        canvas.dispatchEvent(new MouseEvent('click', { ...eventInit, clientX: clientX + 15 }));
        while (performance.now() - started < 32) {}
        window.__canvasMetrics.lastAction = { durationMs: performance.now() - started, attempt, x: fresh.x, y: fresh.y };
        return window.__canvasMetrics.lastAction;
      }
      throw new Error('Circuit breaker could not resolve a fresh canvas coordinate');
    };

    const wsUrl = `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/telemetry`;
    const socket = new WebSocket(wsUrl);
    socket.addEventListener('message', event => {
      const frame = JSON.parse(event.data);
      drawGrid(frame);
      invokeBoundary(frame);
    });
  </script>
</body>
</html>
"""

SHADOW_DOM_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Shadow DOM Accessibility Testbed</title>
  <style>
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; background: #0f172a; color: #e2e8f0; font-family: system-ui, sans-serif; }
  </style>
</head>
<body>
  <closed-shell-host aria-label="Payment operations shell"></closed-shell-host>
  <script>
    class ClosedShellHost extends HTMLElement {
      connectedCallback() {
        const root = this.attachShadow({ mode: 'open' });
        root.innerHTML = `
          <style>
            section { padding: 24px; border: 1px solid #334155; border-radius: 8px; }
            button { padding: 10px 14px; border-radius: 6px; border: 0; background: #22c55e; color: #052e16; font-weight: 700; }
          </style>
          <section role="region" aria-label="Secure transaction control panel">
            <nested-action-host aria-label="Nested transfer action surface"></nested-action-host>
            <div role="status" aria-live="polite">Ready for accessibility tree pathfinding</div>
          </section>`;
      }
    }
    class NestedActionHost extends HTMLElement {
      connectedCallback() {
        const root = this.attachShadow({ mode: 'open' });
        root.innerHTML = `<button role="button" aria-label="Approve isolated replay protection transfer">Approve</button>`;
      }
    }
    customElements.define('closed-shell-host', ClosedShellHost);
    customElements.define('nested-action-host', NestedActionHost);
  </script>
</body>
</html>
"""
