#!/usr/bin/env python3
"""Create a small Codex mission directory for repo-local feature work."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:72] or "mission"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", default=".", help="repo path")
    parser.add_argument("--title", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument(
        "--missions-root",
        default=str(Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "missions"),
    )
    args = parser.parse_args()

    now = datetime.now(timezone.utc).isoformat()
    root = Path(args.missions_root).expanduser()
    dest = root / _slug(args.title)
    dest.mkdir(parents=True, exist_ok=True)

    (dest / "working_directory.txt").write_text(str(Path(args.cwd).resolve()) + "\n")
    (dest / "mission.md").write_text(f"# {args.title}\n\n{args.objective}\n")
    (dest / "features.json").write_text(json.dumps({
        "features": [{
            "id": _slug(args.title),
            "milestone": "implementation",
            "status": "pending",
            "description": args.objective,
        }]
    }, indent=2) + "\n")
    (dest / "validation-contract.md").write_text(
        "# Validation Contract\n\n- Feature-specific tests pass.\n- Full repo test gate passes.\n"
    )
    (dest / "state.json").write_text(json.dumps({
        "missionId": _slug(args.title),
        "state": "active",
        "workingDirectory": str(Path(args.cwd).resolve()),
        "createdAt": now,
        "updatedAt": now,
    }, indent=2) + "\n")
    (dest / "progress_log.jsonl").write_text(json.dumps({
        "timestamp": now,
        "type": "codex_mission_created",
        "message": args.objective,
    }) + "\n")

    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
