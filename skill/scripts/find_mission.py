#!/usr/bin/env python3
"""Find the Factory mission whose working_directory.txt matches a repo path."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", default=".", help="repository path to match")
    default_root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "missions"
    parser.add_argument(
        "--missions-root",
        default=str(default_root),
        help="mission directory; defaults to $CODEX_HOME/missions or ~/.codex/missions",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="print only the mission with the newest state.json updatedAt value",
    )
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()
    missions_root = Path(args.missions_root).expanduser()
    matches: list[tuple[str, Path]] = []

    for marker in missions_root.glob("*/working_directory.txt"):
        try:
            workdir = Path(marker.read_text().strip()).resolve()
        except OSError:
            continue
        if workdir == cwd:
            updated_at = ""
            try:
                state = json.loads((marker.parent / "state.json").read_text())
                updated_at = state.get("updatedAt", "")
            except (OSError, json.JSONDecodeError):
                pass
            matches.append((updated_at, marker.parent))

    matches = sorted(matches, key=lambda item: (item[0], str(item[1])))
    if args.latest and matches:
        print(matches[-1][1])
        return 0

    for _, match in matches:
        print(match)

    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
