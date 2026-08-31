"""Capture feature screenshots of the running app for the pitch deck.

Drives a real session through every feature moment. Writes PNGs OUTSIDE the
project (dev watcher reloads on in-project .png writes — see D-004).

Usage: .venv/bin/python scripts/capture_features.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
OUT = Path.home() / ".kerb" / "pitch"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "http://localhost:3100"

from playwright.sync_api import sync_playwright  # noqa: E402


def shoot(page, name):
    page.wait_for_timeout(700)
    page.screenshot(path=str(OUT / name))
    print("captured", name)


def find_button(page, text):
    return page.locator("button", has_text=text).first


def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1440, "height": 900})
        page.set_default_timeout(20000)
        page.goto(BASE)
        page.wait_for_selector('[data-guide="claims.search"]')
        page.wait_for_timeout(1500)

        # Scene 1 — compile a plan, Guide mode
        find_button(page, "Ask").click()
        page.locator("button.cmd-sug", has_text="#4821").click()
        page.wait_for_selector(".stp", timeout=30000)
        shoot(page, "01-guide-plan.png")

        # Scene 2 — guide advancement into the refund modal
        page.locator('[data-guide="claims.search"]').fill("4821")
        page.wait_for_timeout(600)
        page.locator('[data-guide="claims.row.open"]').click()
        page.wait_for_timeout(600)
        page.locator('[data-guide="claims.refund.start"]').click()
        shoot(page, "02-guide-modal-spotlight.png")

        # Scene 3 — Copilot: confirm-driven steps up to the weakly-grounded memo
        page.locator("button.dial-btn", has_text="Copilot").click()
        page.wait_for_timeout(500)
        for _ in range(2):  # amount, reason -> memo becomes current
            find_button(page, "Confirm & do this step").click()
            page.wait_for_timeout(700)
        shoot(page, "03-copilot-confirm-gate.png")

        # Scene 4 — Autopilot: sandbox rehearsal receipt
        page.locator("button.dial-btn", has_text="Autopilot").click()
        page.wait_for_timeout(500)
        find_button(page, "Rehearse in sandbox").click()
        page.wait_for_selector(".rcp", timeout=90000)
        page.locator(".rail").evaluate("el => el.scrollTop = el.scrollHeight")
        shoot(page, "04-sandbox-receipt.png")

        # Scene 5 — Autopilot live: input frozen + confidence gate
        find_button(page, "Run live").click()
        page.wait_for_selector(".gate", timeout=30000)
        shoot(page, "05-autopilot-live-gate.png")
        find_button(page, "Confirm — proceed").click()
        page.wait_for_selector(".done", timeout=30000)
        shoot(page, "06-autopilot-complete.png")

        # Scene 6 — Sentinel: judge sabotage -> self-heal
        find_button(page, "Sentinel").click()
        page.wait_for_selector(".sab", timeout=10000)
        page.locator('.sab input:not([type="checkbox"])').fill("Release Funds")
        page.locator('.sab input[type="checkbox"]').check()
        find_button(page, "Apply sabotage").click()
        page.wait_for_timeout(600)
        find_button(page, "Run Sentinel").click()
        deadline = time.time() + 150
        while time.time() < deadline:
            body = page.locator(".sentinel").inner_text()
            if "HEALED" in body or "ESCALATED" in body.upper():
                break
            page.wait_for_timeout(2000)
        shoot(page, "07-sentinel-healed.png")

        # Scene 7 — escalation on the disputed claim
        find_button(page, "Sentinel").click()
        find_button(page, "Ask").click()
        page.locator("button.cmd-sug", has_text="#5150").click()
        page.wait_for_selector(".esc-card", timeout=30000)
        shoot(page, "08-escalation-card.png")

        b.close()
        print("all captures in", OUT)


if __name__ == "__main__":
    main()
