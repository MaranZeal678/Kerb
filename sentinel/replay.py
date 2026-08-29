"""Sentinel replay runner — replays every stored Guide Plan in a fresh Runloop devbox.

Loop: launch devbox from snapshot (app + playwright preinstalled) → run plan steps
headlessly → capture per-step screenshots + DOM snapshot on failure → red/green board.

STATUS: scaffold. Tier 2.2/2.4. Spike the devbox hello-world FIRST (see ROADMAP §sequencing).
"""


def replay_plan(plan: dict) -> dict:
    """Return {plan_id, status: green|red, failed_step, dom_snapshot, screenshots}."""
    raise NotImplementedError("Tier 2.4")
