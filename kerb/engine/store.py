"""Plan store — JSON files, boring by default (spec eng review)."""

import json
from pathlib import Path

PLANS = Path(__file__).parents[2] / "plans"


def save_plan(plan: dict) -> None:
    PLANS.mkdir(parents=True, exist_ok=True)
    (PLANS / f"{plan['plan_id']}.json").write_text(json.dumps(plan, indent=1))


def load_plans() -> list[dict]:
    if not PLANS.exists():
        return []
    return [json.loads(f.read_text()) for f in sorted(PLANS.glob("pln_*.json"))]


def clear_plans() -> None:
    for f in PLANS.glob("pln_*.json"):
        f.unlink()
