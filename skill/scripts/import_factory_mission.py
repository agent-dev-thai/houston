#!/usr/bin/env python3
"""Mirror a Factory mission into the Codex global mission directory."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path


CORE_FILES = (
    "working_directory.txt",
    "mission.md",
    "architecture.md",
    "AGENTS.md",
    "features.json",
    "validation-contract.md",
    "validation-state.json",
)


def _safe_name(source: Path) -> str:
    try:
        state = json.loads((source / "state.json").read_text())
        mission_id = state.get("missionId")
        if mission_id:
            return str(mission_id)
    except (OSError, json.JSONDecodeError):
        pass
    return source.name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("factory_mission", help="path to a Factory mission directory")
    parser.add_argument(
        "--missions-root",
        default=str(Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "missions"),
        help="Codex missions root; defaults to $CODEX_HOME/missions or ~/.codex/missions",
    )
    parser.add_argument("--name", help="destination mission directory name")
    parser.add_argument("--force", action="store_true", help="overwrite existing mirrored files")
    args = parser.parse_args()

    source = Path(args.factory_mission).expanduser().resolve()
    if not source.is_dir():
        raise SystemExit(f"not a directory: {source}")

    root = Path(args.missions_root).expanduser()
    dest = root / (args.name or _safe_name(source))
    dest.mkdir(parents=True, exist_ok=True)

    for name in CORE_FILES:
        src = source / name
        if not src.exists():
            continue
        dst = dest / name
        if dst.exists() and not args.force:
            continue
        shutil.copy2(src, dst)

    for dirname in ("library", "contract-work"):
        src_dir = source / dirname
        if not src_dir.is_dir():
            continue
        dst_dir = dest / dirname
        if dst_dir.exists() and args.force:
            shutil.rmtree(dst_dir)
        if not dst_dir.exists():
            shutil.copytree(src_dir, dst_dir)

    state = {}
    state_path = dest / "state.json"
    if state_path.exists() and not args.force:
        try:
            state = json.loads(state_path.read_text())
        except json.JSONDecodeError:
            state = {}
    else:
        source_state = {}
        try:
            source_state = json.loads((source / "state.json").read_text())
        except (OSError, json.JSONDecodeError):
            pass
        state = {
            "missionId": source_state.get("missionId", dest.name),
            "state": "imported",
            "workingDirectory": source_state.get("workingDirectory"),
        }

    state["sourceFactoryMission"] = str(source)
    state["updatedAt"] = datetime.now(timezone.utc).isoformat()
    state_path.write_text(json.dumps(state, indent=2) + "\n")

    progress = dest / "progress_log.jsonl"
    with progress.open("a") as fh:
        fh.write(json.dumps({
            "timestamp": state["updatedAt"],
            "type": "factory_mission_imported",
            "sourceFactoryMission": str(source),
        }) + "\n")

    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
