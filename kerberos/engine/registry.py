"""Approved selector registry — the single source of truth for where the AI may act.

The planner is prompted only with logical ids; raw CSS never reaches the model.
Sentinel's repair agent patches this table (as new versions) when the UI drifts.

STATUS: scaffold. Entries below are the planned Meridian instrumentation set.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Control:
    id: str                      # logical name the planner sees, e.g. "claims.refund.reason_code"
    selector: str                # css, always via data-guide
    label: str                   # human label shown on step cards
    actions: tuple = ("click",)  # allowed actions: click | fill | select
    version: int = 1


REGISTRY: dict[str, Control] = {
    c.id: c
    for c in [
        Control("claims.search", '[data-guide="claims.search"]', "Claim search box", ("fill",)),
        Control("claims.row.open", '[data-guide="claims.row.open"]', "Open claim", ("click",)),
        Control("claims.refund.start", '[data-guide="claims.refund.start"]', "Start refund", ("click",)),
        Control("claims.refund.amount", '[data-guide="claims.refund.amount"]', "Refund amount", ("fill",)),
        Control("claims.refund.reason_code", '[data-guide="claims.refund.reason_code"]', "Reason code", ("select",)),
        Control("claims.refund.memo", '[data-guide="claims.refund.memo"]', "Supervisor memo", ("fill",)),
        Control("claims.refund.approve", '[data-guide="claims.refund.approve"]', "Approve refund", ("click",)),
    ]
}


def planner_view() -> list[dict]:
    """What the model is allowed to know: logical ids, labels, allowed actions. No CSS."""
    return [{"id": c.id, "label": c.label, "actions": list(c.actions)} for c in REGISTRY.values()]
