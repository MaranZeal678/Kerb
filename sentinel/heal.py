"""Self-heal repair agent — turns a red Sentinel replay into a registry patch.

Input: failed step + old registry entry + fresh DOM snapshot from the devbox.
Mistral proposes a patch (new selector/label for the logical id). The patch is only
merged after (1) validator passes and (2) a re-replay in a fresh devbox goes green.

This is the wow feature: docs/DEMO_SCRIPT.md §2:15.

STATUS: scaffold. Tier 2.5.
"""


def propose_patch(failed_step: dict, dom_snapshot: str) -> dict:
    """Return {control_id, new_selector, new_label, rationale} for validator + re-replay."""
    raise NotImplementedError("Tier 2.5")
