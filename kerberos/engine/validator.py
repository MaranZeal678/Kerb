"""Server-side validator — pure Python, no LLM. Nothing renders or executes without this.

Rules V1-V7 (spec §4.4). Failures are named strings surfaced to the user as cards.
"""

from . import registry as regmod

MAX_STEPS = 12
GROUND_AUTO = 0.75
ENTRY_ROUTE = "claims"


def validate_plan(plan: dict) -> list[str]:
    errs: list[str] = []
    reg = regmod.registry()
    steps = plan.get("steps", [])
    if len(steps) > MAX_STEPS:
        errs.append(f"V6: plan has {len(steps)} steps — over the {MAX_STEPS}-step latency budget")
    route = ENTRY_ROUTE
    for s in steps:
        sid, act = s.get("selector"), s.get("action")
        c = reg.get(sid)
        if c is None:
            errs.append(f"V1: step {s.get('id')}: unknown selector '{sid}'")
            continue
        if act not in c.actions:
            errs.append(f"V2: step {s.get('id')}: action '{act}' not allowed on '{sid}' (allows {c.actions})")
        if act in ("fill", "select") and not str(s.get("value") or "").strip():
            errs.append(f"V3: step {s.get('id')}: action '{act}' requires a value")
        if sid == "claims.refund.reason_code" and s.get("value") and not str(s["value"]).startswith("RC-"):
            errs.append(f"V3: step {s.get('id')}: '{s['value']}' is not a reason code")
        if s.get("route") != route:
            errs.append(f"V4: step {s.get('id')}: declared route '{s.get('route')}' but app would be on "
                        f"'{route}' — unreachable page state")
        if (route, sid) in regmod.TRANSITIONS and act == "click":
            route = regmod.TRANSITIONS[(route, sid)]
        ceiling = s.get("autonomy_ceiling")
        if ceiling not in ("guide", "copilot", "autopilot", None):
            errs.append(f"V5: step {s.get('id')}: invalid autonomy ceiling '{ceiling}'")
        if ceiling == "autopilot" and (s.get("grounding") or 0) < GROUND_AUTO:
            errs.append(f"V5: step {s.get('id')}: grounding {s.get('grounding')} below autopilot threshold")
    return errs


def validate_patch(patch: dict) -> list[str]:
    errs = []
    reg = regmod.registry()
    if patch.get("control_id") not in reg:
        errs.append(f"V1: patch targets unknown control '{patch.get('control_id')}'")
    if not str(patch.get("new_guide") or "").strip():
        errs.append("V7: patch has no new selector")
    if not patch.get("evidence"):
        errs.append("V7: patch carries no evidence")
    return errs
