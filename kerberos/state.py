"""Global Reflex state — the autonomy dial IS this state.

One validated Guide Plan, one mode var; every mode is a projection of the same plan.

STATUS: scaffold. Wire to engine in Tier 1.5–1.7.
"""

import reflex as rx


class KerberosState(rx.State):
    mode: str = "guide"           # guide | copilot | autopilot
    goal: str = ""
    plan: list[dict] = []         # validated Guide Plan steps
    current_step: int = 0
    executing: bool = False
    receipt: dict = {}            # Runloop dry-run execution receipt (autopilot)

    def set_mode(self, mode: str):
        self.mode = mode

    async def submit_goal(self, goal: str):
        """Compile + validate a plan for the goal, then stream steps to the overlay."""
        raise NotImplementedError("Tier 1.5")
