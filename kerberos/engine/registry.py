"""Approved selector registry — the single source of truth for where the AI may act.

The planner is prompted only with logical ids via planner_view(); CSS lives here alone.
Sentinel's repair agent appends versioned PATCHES (never edits BASE); every patch
carries evidence and a green re-replay proof (spec §4.2, V7).
"""

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

# Patches persist on disk so every process — backend, replay subprocesses,
# CLI — sees the same registry version (and the trail survives restarts).
PATCHES_FILE = Path(os.environ.get("KERBEROS_STATE_DIR",
                                   Path.home() / ".kerberos")) / "registry_patches.json"


@dataclass(frozen=True)
class Control:
    id: str        # logical name the planner sees
    guide: str     # current data-guide attribute value in the DOM
    label: str
    tag: str       # button | input | select | textarea
    actions: tuple
    route: str     # claims | claim
    region: str    # claims-list | claim-detail | refund-modal

    @property
    def selector(self) -> str:
        return f'[data-guide="{self.guide}"]'


BASE = [
    Control("claims.search", "claims.search", "Claim search", "input", ("fill",), "claims", "claims-list"),
    Control("claims.filter.status", "claims.filter.status", "Status filter", "select", ("select",), "claims", "claims-list"),
    Control("claims.row.open", "claims.row.open", "Open claim", "button", ("click",), "claims", "claims-list"),
    Control("claims.refund.start", "claims.refund.start", "Start refund", "button", ("click",), "claim", "claim-detail"),
    Control("claims.notes.add", "claims.notes.add", "Add note", "input", ("fill",), "claim", "claim-detail"),
    Control("claims.status.set", "claims.status.set", "Set status", "select", ("select",), "claim", "claim-detail"),
    Control("claims.docs.open", "claims.docs.open", "Open documents", "button", ("click",), "claim", "claim-detail"),
    Control("claims.refund.amount", "claims.refund.amount", "Refund amount", "input", ("fill",), "claim", "refund-modal"),
    Control("claims.refund.reason_code", "claims.refund.reason_code", "Reason code", "select", ("select",), "claim", "refund-modal"),
    Control("claims.refund.memo", "claims.refund.memo", "Supervisor memo", "textarea", ("fill",), "claim", "refund-modal"),
    Control("claims.refund.approve", "claims.refund.approve", "Approve refund", "button", ("click",), "claim", "refund-modal"),
    Control("claims.refund.cancel", "claims.refund.cancel", "Cancel", "button", ("click",), "claim", "refund-modal"),
]

# Route transitions a click can cause: (route_before, control_id) -> route_after (validator V4)
TRANSITIONS = {
    ("claims", "claims.row.open"): "claim",
}

def _load_patches() -> list[dict]:
    try:
        return json.loads(PATCHES_FILE.read_text())
    except Exception:
        return []


def _save_patches(patches: list[dict]) -> None:
    PATCHES_FILE.parent.mkdir(parents=True, exist_ok=True)
    PATCHES_FILE.write_text(json.dumps(patches, indent=1))


def registry() -> dict[str, Control]:
    reg = {c.id: c for c in BASE}
    for p in _load_patches():
        c = reg[p["control_id"]]
        reg[c.id] = Control(c.id, p["new_guide"], p.get("new_label") or c.label,
                            c.tag, c.actions, c.route, c.region)
    return reg


def version() -> int:
    return 1 + len(_load_patches())


def planner_view() -> list[dict]:
    """What the model may know: logical ids, labels, actions, routes. Never CSS."""
    return [{"id": c.id, "label": c.label, "actions": list(c.actions), "route": c.route}
            for c in registry().values()]


def apply_patch(patch: dict) -> None:
    patch.setdefault("ts", time.time())
    patches = _load_patches()
    patches.append(patch)
    _save_patches(patches)


def rollback_last() -> None:
    patches = _load_patches()
    if patches:
        patches.pop()
        _save_patches(patches)
