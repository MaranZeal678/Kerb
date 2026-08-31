"""Sandbox execution: one interface, two adapters (spec §5.2, §7).

- LocalSandbox (ACTIVE — decision D-001): headless Chromium via Playwright in an
  isolated browser session against the app. Same contract as the devbox path.
- RunloopSandbox (key-ready stub): swaps in when RUNLOOP_API_KEY exists.

The live executor lives in kerb/state.py (it mutates Reflex state directly).
"""

import os
import time
from pathlib import Path

from . import registry as regmod

# Receipts live OUTSIDE the project tree: the dev file-watcher hot-reloads on
# .png writes, which drops every websocket mid-replay (see docs/DECISIONS.md D-004).
RECEIPTS = Path(os.environ.get("KERB_RECEIPTS_DIR",
                               Path.home() / ".kerb" / "receipts"))

_DOM_JS = """els => els.map(e => {
  const r = e.closest('[data-region]');
  return {guide: e.getAttribute('data-guide'), tag: e.tagName.toLowerCase(),
          text: (e.innerText || e.value || '').slice(0, 60),
          region: r ? r.getAttribute('data-region') : null};
})"""


_LOG = Path("/tmp/kerb-sandbox.log")


def _log(msg: str) -> None:
    with _LOG.open("a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def sandbox_replay(plan: dict, base_url: str) -> dict:
    """Run the full plan headlessly in a fresh browser session. Returns
    {status: green|red, steps: [...], failed_step, dom_controls, after}."""
    from playwright.sync_api import sync_playwright

    reg = regmod.registry()
    out = RECEIPTS / plan["plan_id"]
    out.mkdir(parents=True, exist_ok=True)
    result = {"plan_id": plan["plan_id"], "goal": plan["goal"], "status": "green",
              "steps": [], "failed_step": None, "dom_controls": None, "after": ""}
    _log(f"replay start {plan['plan_id']} -> {base_url}")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1360, "height": 900})
        page.set_default_timeout(8000)
        page.on("websocket", lambda ws: (_log(f"ws open {ws.url[-30:]}"),
                                         ws.on("close", lambda w: _log("ws CLOSED"))))
        page.on("console", lambda m: _log(f"console[{m.type}] {m.text[:100]}")
                if m.type in ("error", "warning") else None)
        try:
            page.goto(base_url, timeout=30000)
            page.wait_for_selector('[data-guide="claims.search"]', timeout=25000)
            _log("hydrated")
            for s in plan["steps"]:
                sel = reg[s["selector"]].selector

                def _do_step():
                    loc = page.locator(sel)
                    loc.wait_for(state="visible", timeout=5000)
                    if s["action"] == "fill":
                        loc.fill(str(s["value"]), timeout=8000)
                    elif s["action"] == "select":
                        loc.select_option(str(s["value"]), timeout=8000)
                    else:
                        loc.click(timeout=8000)
                    page.wait_for_timeout(650)
                    # verify the action landed: a click that opens UI must change the DOM;
                    # for fills/selects, trust the roundtrip wait
                try:
                    try:
                        _do_step()
                    except Exception:
                        _log(f"step {s['id']} transient retry")
                        page.wait_for_timeout(1200)
                        _do_step()
                    page.screenshot(path=str(out / f"step_{s['id']}.png"))
                    result["steps"].append({"id": s["id"], "status": "ok", "why": s["why"]})
                    _log(f"step {s['id']} ok")
                except Exception as e:
                    _log(f"step {s['id']} FAIL {type(e).__name__}: {str(e)[:120]}")
                    result["status"] = "red"
                    result["failed_step"] = s["id"]
                    result["steps"].append({"id": s["id"], "status": "failed",
                                            "why": s["why"], "note": type(e).__name__})
                    try:
                        result["dom_controls"] = page.eval_on_selector_all("[data-guide]", _DOM_JS)
                        page.screenshot(path=str(out / f"step_{s['id']}_FAILED.png"))
                    except Exception as e2:
                        _log(f"evidence capture failed: {e2}")
                    break
            if result["status"] == "green":
                try:
                    result["after"] = page.locator('[data-field="claim-status"]').inner_text(timeout=2000)
                except Exception:
                    result["after"] = ""
        finally:
            browser.close()
    _log(f"replay done {result['status']}")
    return result


class RunloopSandbox:
    """Devbox adapter — activates when RUNLOOP_API_KEY is present (spec §7.1-7.3)."""

    def __init__(self):
        self.key = os.environ.get("RUNLOOP_API_KEY")

    def replay(self, plan: dict, base_url: str) -> dict:
        if not self.key:
            raise RuntimeError("RUNLOOP_API_KEY not set — decision D-001 fallback applies")
        raise NotImplementedError("Devbox blueprint wiring: spec §7.1; enable when a key exists")


def subprocess_replay(plan: dict, base_url: str) -> dict:
    """Run the replay in its own OS process — full isolation from the backend's
    event loop and threads (and the closest local analogue to a devbox)."""
    import json
    import subprocess
    import sys
    import tempfile

    root = Path(__file__).parents[2]
    py = root / ".venv" / "bin" / "python"
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(plan, f)
        plan_path = f.name
    env = dict(os.environ)
    # CRITICAL: without this, the child regenerates __pycache__ inside the project,
    # the dev file-watcher hot-reloads the backend, and every websocket (including
    # the sandbox session's) drops mid-replay. Cost one afternoon; do not remove.
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        proc = subprocess.run(
            [str(py if py.exists() else sys.executable), str(root / "scripts" / "replay_cli.py"),
             plan_path, base_url],
            capture_output=True, text=True, timeout=150, cwd=str(root), env=env)
        if proc.returncode != 0:
            _log(f"subprocess replay rc={proc.returncode}: {proc.stderr[-300:]}")
            return {"plan_id": plan["plan_id"], "goal": plan["goal"], "status": "red",
                    "steps": [], "failed_step": None, "dom_controls": None,
                    "after": "", "error": proc.stderr[-200:]}
        return json.loads(proc.stdout.strip().splitlines()[-1])
    finally:
        os.unlink(plan_path)


def replay(plan: dict, base_url: str) -> dict:
    if os.environ.get("RUNLOOP_API_KEY"):
        try:
            return RunloopSandbox().replay(plan, base_url)
        except NotImplementedError:
            pass
    return subprocess_replay(plan, base_url)
