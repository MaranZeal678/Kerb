"""Plan compiler: goal + retrieved policy chunks + registry planner_view -> Guide Plan (JSON).

Uses Mistral chat with JSON-constrained output. The model only ever sees logical
control ids from registry.planner_view() — it cannot reference anything else.

STATUS: scaffold. Implement in Tier 1.4.
"""


def compile_plan(goal: str) -> dict:
    """RAG-retrieve → prompt Mistral → parse Guide Plan → attach grounding scores.

    Returns a plan dict shaped as documented in docs/ARCHITECTURE.md, ready for
    validator.validate_plan(). Raises PlanRejected if validation fails.
    """
    raise NotImplementedError("Tier 1.4")
