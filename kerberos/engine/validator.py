"""Server-side plan validator — pure Python, no LLM. Nothing renders or executes without passing this.

STATUS: scaffold with the real rule set; wire to planner output in Tier 1.2.
"""

from .registry import REGISTRY

AUTONOMY_LEVELS = ("guide", "copilot", "autopilot")
AUTOPILOT_MIN_GROUNDING = 0.75


def validate_plan(plan: dict) -> list[str]:
    """Return a list of violations; empty list means the plan is admissible."""
    errors: list[str] = []
    for step in plan.get("steps", []):
        sid = step.get("selector")
        control = REGISTRY.get(sid)
        if control is None:
            errors.append(f"step {step.get('id')}: unknown selector '{sid}'")
            continue
        if step.get("action") not in control.actions:
            errors.append(f"step {step.get('id')}: action '{step.get('action')}' not allowed on '{sid}'")
        if step.get("max_autonomy") not in AUTONOMY_LEVELS:
            errors.append(f"step {step.get('id')}: invalid max_autonomy")
        grounding = step.get("grounding_score", 0.0)
        if step.get("max_autonomy") == "autopilot" and grounding < AUTOPILOT_MIN_GROUNDING:
            errors.append(
                f"step {step.get('id')}: grounding {grounding:.2f} below autopilot threshold "
                f"{AUTOPILOT_MIN_GROUNDING} — demote to copilot"
            )
    return errors
