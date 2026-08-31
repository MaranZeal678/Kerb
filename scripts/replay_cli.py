"""Sandbox replay CLI — one isolated process per rehearsal/verification run.

Usage: python scripts/replay_cli.py <plan.json path> <base_url>
Prints the replay result as JSON on stdout (last line).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[1] / ".env")

from kerb.engine.executor import sandbox_replay  # noqa: E402


def main() -> None:
    plan = json.loads(Path(sys.argv[1]).read_text())
    base_url = sys.argv[2]
    result = sandbox_replay(plan, base_url)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
