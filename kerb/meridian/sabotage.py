"""Judge-driven sabotage (spec §6.6) — module-level so every browser session,
including the sandbox's Playwright session, sees the same broken world.

Renaming a control changes BOTH its visible label and its data-guide attribute
(simulating a developer renaming the hook) — that is what genuinely breaks the
stored plans. Moves swap the approve button between real layout slots.
"""

import re

OVERRIDES: dict[str, dict] = {}   # control_id -> {"label": str, "guide": str, "moved": bool}


def _slug(label: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return s or "renamed-control"


def apply(control_id: str, new_label: str, move: bool = False) -> None:
    OVERRIDES[control_id] = {"label": new_label, "guide": _slug(new_label), "moved": move}


def reset() -> None:
    OVERRIDES.clear()


def eff(control_id: str, base_label: str) -> tuple[str, str, bool]:
    """(visible label, data-guide value, moved?) for a control right now."""
    o = OVERRIDES.get(control_id)
    if not o:
        return base_label, control_id, False
    return o["label"], o["guide"], o["moved"]
