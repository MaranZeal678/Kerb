"""Sentinel (spec §6.1-6.3): re-run every stored plan in a sandbox; on red, invoke the
repair agent; merge a patch only after it passes the validator AND a green re-replay.
"""

from kerb.engine import registry as regmod
from kerb.engine.executor import replay as sandbox_replay
from kerb.engine.validator import validate_patch

from . import heal


def check_plan(plan: dict, base_url: str) -> dict:
    """Returns a board tile: {plan_id, goal, status, failed_step?, patch?, proof?, detail}."""
    tile = {"plan_id": plan["plan_id"], "goal": plan["goal"], "status": "checking",
            "failed_step": None, "patch": None, "proof": "", "detail": ""}
    r = sandbox_replay(plan, base_url)
    if r["status"] == "green":
        tile.update(status="green", detail=f"{len(r['steps'])} steps re-ran clean · {r.get('after','')}")
        return tile
    tile.update(status="red", failed_step=r["failed_step"],
                detail=f"step {r['failed_step']} failed — control did not resolve")
    patch = heal.propose_patch(plan, r["failed_step"], r["dom_controls"])
    if patch is None:
        tile.update(status="escalated",
                    detail=f"step {r['failed_step']}: no evidence-compatible replacement in the DOM — "
                           "handoff filed instead of guessing")
        return tile
    errs = validate_patch(patch)
    if errs:
        tile.update(status="escalated", detail="; ".join(errs))
        return tile
    regmod.apply_patch(patch)             # provisional
    r2 = sandbox_replay(plan, base_url)   # green re-replay gate
    if r2["status"] == "green":
        patch["proof"] = f"re-replay green: {len(r2['steps'])} steps · registry v{regmod.version()}"
        tile.update(status="healed", patch=patch, proof=patch["proof"],
                    detail=f"'{patch['old_guide']}' → '{patch['new_guide']}'")
    else:
        regmod.rollback_last()
        tile.update(status="escalated", patch=patch,
                    detail="proposed patch failed its green re-replay — rolled back, handoff filed")
    return tile
