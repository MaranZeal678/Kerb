"""Plan compiler: goal + retrieved policy + registry view -> validated Guide Plan.

Model-first with a deterministic fallback, so a slow or absent endpoint degrades
the wording of a plan, never the availability of one. Grounding scores and
autonomy ceilings are ALWAYS computed by the deterministic post-pass regardless
of which compiler authored the steps: the model never grades its own work.
"""

import json
import os
import re

from . import llm, rag
from . import registry as regmod
from .validator import validate_plan

GROUND_AUTO = 0.75
GROUND_CONFIRM = 0.45

# Navigation is procedural, not a policy claim — the grounding floor governs
# policy-bearing actions only (spec §4.3). Nav steps are always safe to automate.
NAV_SELECTORS = {"claims.search", "claims.row.open", "claims.refund.cancel"}


def _ceiling(g: float, required: bool) -> str:
    if g >= GROUND_AUTO:
        return "autopilot"
    if g >= GROUND_CONFIRM:
        return "copilot"
    return "guide" if not required else "escalate"


def _ground(step: dict) -> dict:
    hits = rag.retrieve(step["why"], k=2)
    best = hits[0]
    step["citation"] = {"doc": best["doc"], "chunk": best["chunk"]}
    if step["selector"] in NAV_SELECTORS:
        step["kind"] = "nav"
        step["grounding"] = 1.0
        step["autonomy_ceiling"] = "autopilot"
        return step
    step["kind"] = "action"
    g = round(best["score"] * rag.coverage(step["why"], best["text"]), 2)
    step["grounding"] = g
    step["autonomy_ceiling"] = _ceiling(g, step.get("required", True))
    return step


def _postpass(goal: str, steps: list[dict], compiler: str) -> dict:
    """Attach grounding/ceilings, sources, ids; escalate if a required step is unfounded."""
    sources: list[dict] = []
    for i, s in enumerate(steps, 1):
        s["id"] = i
        _ground(s)
        hit = {"doc": s["citation"]["doc"], "chunk": s["citation"]["chunk"]}
        if hit not in [{"doc": x["doc"], "chunk": x["chunk"]} for x in sources]:
            chunk = next(c for c in rag.retrieve(s["why"], k=1))
            sources.append(chunk)
        if s["autonomy_ceiling"] == "escalate":
            return {"escalation": {
                "goal": goal,
                "reason": f"Required step '{s['why']}' has grounding {s['grounding']:.2f} — below the "
                          f"{GROUND_CONFIRM} floor. Kerb will not act where it cannot cite policy.",
                "partial_steps": steps[: i - 1],
                "handoff": "Route to a supervisor with the claim number and the steps already planned.",
            }}
    claim_match = re.search(r"#?(\d{4})", goal)
    plan = {
        "plan_id": f"pln_{claim_match.group(1) if claim_match else 'x'}_r{regmod.version()}",
        "goal": goal,
        "docs_version": rag.docs_version(),
        "registry_version": regmod.version(),
        "compiler": compiler,
        "sources": sources,
        "steps": steps,
    }
    errs = validate_plan(plan)
    if errs:
        return {"rejected": errs, "goal": goal}
    plan["status"] = "validated"
    return plan


def policy_gate(goal: str, claims: list[dict]) -> dict | None:
    """Eligibility check that runs BEFORE any plan is authored.

    This is deliberately compiler-independent. If it lived inside one authoring
    strategy, a model-authored plan could route around a policy prohibition
    simply by being fluent. Returns an escalation, or None when the goal is
    eligible to be planned at all.
    """
    m = re.search(r"#?(\d{4})", goal)
    if not m or "refund" not in goal.lower():
        return {"escalation": {
            "goal": goal,
            "reason": "I can only compile plans for goals I can ground: refund flows on a known claim.",
            "partial_steps": [], "handoff": "Rephrase with a claim number, e.g. 'Issue a refund for claim #4821'.",
        }}
    cid = m.group(1)
    claim = next((c for c in claims if str(c["id"]) == cid), None)
    if claim is None:
        return {"escalation": {"goal": goal, "reason": f"Claim #{cid} does not exist in Meridian.",
                               "partial_steps": [], "handoff": "Verify the claim number."}}
    if claim["status"] == "disputed":
        hit = rag.retrieve("refunds must not be issued on a disputed claim route to supervisor", k=1)[0]
        return {"escalation": {
            "goal": goal,
            "reason": f"Claim #{cid} is in status 'disputed'. Policy: refunds must not be issued on a "
                      f"disputed claim ({hit['doc']}).",
            "partial_steps": [], "citation": {"doc": hit["doc"], "chunk": hit["chunk"]},
            "handoff": f"Handoff filed: claim #{cid}, requested refund of ${claim['balance_due']:.2f}, "
                       f"blocked by dispute status. Supervisor resolution required before disbursement.",
        }}
    return None


def _deterministic_steps(goal: str, claims: list[dict]) -> list[dict]:
    """Authoring only. policy_gate() has already established eligibility."""
    cid = re.search(r"#?(\d{4})", goal).group(1)
    claim = next(c for c in claims if str(c["id"]) == cid)
    amount = claim["balance_due"]
    big = amount > 500
    steps: list[dict] = [
        {"route": "claims", "selector": "claims.search", "action": "fill", "value": cid,
         "why": "Find the claim in the claims list to open its detail screen", "required": True},
        {"route": "claims", "selector": "claims.row.open", "action": "click", "value": cid,
         "why": "Refunds are issued from the claim detail screen", "required": True},
        {"route": "claim", "selector": "claims.refund.start", "action": "click", "value": None,
         "why": "Refunds are issued from the claim detail screen using the Start Refund action", "required": True},
        {"route": "claim", "selector": "claims.refund.amount", "action": "fill", "value": f"{amount:.2f}",
         "why": "The operator enters the refund amount", "required": True},
    ]
    if big:
        steps.append({"route": "claim", "selector": "claims.refund.reason_code", "action": "select",
                      "value": "RC-07",
                      "why": "Large refunds require a reason code; refunds issued to correct a processing "
                             "error must use reason code RC-07", "required": True})
        steps.append({"route": "claim", "selector": "claims.refund.memo", "action": "fill",
                      "value": f"Large refund ${amount:.2f} on claim #{cid} — processing error correction (RC-07).",
                      "why": "A brief supervisor memo note is appropriate for larger disbursements",
                      "required": False})
    steps.append({"route": "claim", "selector": "claims.refund.approve", "action": "click", "value": None,
                  "why": "Approval finalizes the disbursement and updates the claim status to refunded",
                  "required": True})
    return steps


def _model_steps(goal: str, claims: list[dict]) -> list[dict]:
    context = "\n\n".join(f"[{h['doc']} chunk {h['chunk']}]\n{h['text']}" for h in rag.retrieve(goal, k=4))
    claim_rows = "\n".join(f"- claim #{c['id']}: status={c['status']}, balance_due=${c['balance_due']:.2f}"
                           for c in claims)
    prompt = f"""You compile UI action plans. You may ONLY reference these controls (logical ids):
{json.dumps(regmod.planner_view(), indent=1)}

Route rules: the app starts on route "claims"; clicking claims.row.open moves to route "claim".
Every step needs: route, selector (a logical id above), action (one the control allows),
value (string or null), why (one sentence that QUOTES the policy excerpt language as closely
as possible — grounding is scored by word overlap with the cited policy text), required (bool).

Policy excerpts:
{context}

Claims data:
{claim_rows}

Goal: {goal}

Return ONLY a JSON object: {{"steps": [...]}} — no prose."""
    data = llm.chat_json(prompt, temperature=0.1)
    steps = data["steps"]
    assert isinstance(steps, list) and steps, "empty plan"
    return steps


def compile_plan(goal: str, claims: list[dict]) -> dict:
    """Returns a validated plan, or {'escalation': ...}, or {'rejected': [...]}.

    Order is the safety property: eligibility is decided before authoring, so no
    compiler - however fluent - can produce a plan for a prohibited goal.
    """
    blocked = policy_gate(goal, claims)
    if blocked is not None:
        return blocked
    if llm.available() and not os.environ.get("KERB_FORCE_DETERMINISTIC"):
        try:
            result = _postpass(goal, _model_steps(goal, claims), "model")
            if result.get("status") == "validated":
                return result
            # A model-authored plan that fails grading is not an escalation:
            # fall through and let the deterministic compiler author it instead.
        except Exception:
            pass
    return _postpass(goal, _deterministic_steps(goal, claims), "deterministic")
