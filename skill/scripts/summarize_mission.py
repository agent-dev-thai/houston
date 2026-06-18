#!/usr/bin/env python3
"""Print a compact summary of a Codex mission directory."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def _load_json(path: Path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mission_dir")
    parser.add_argument("--tail", type=int, default=8)
    args = parser.parse_args()

    mission_dir = Path(args.mission_dir).expanduser().resolve()
    features = _load_json(mission_dir / "features.json", {}).get("features", [])
    state = _load_json(mission_dir / "state.json", {})
    counts = Counter(feature.get("status", "unknown") for feature in features)

    print(f"mission_dir: {mission_dir}")
    print(f"state: {state.get('state', 'unknown')}")
    print(f"working_directory: {state.get('workingDirectory', 'unknown')}")
    print("features:")
    for status, count in sorted(counts.items()):
        ids = [f.get("id", "?") for f in features if f.get("status", "unknown") == status]
        print(f"  {status}: {count} ({', '.join(ids)})")

    log_path = mission_dir / "progress_log.jsonl"
    if log_path.exists():
        lines = log_path.read_text(errors="replace").splitlines()[-args.tail :]
        print("recent_progress:")
        for line in lines:
            try:
                event = json.loads(line)
                summary = event.get("message") or event.get("featureId") or event.get("type")
                print(f"  {event.get('timestamp', '?')} {event.get('type', '?')}: {summary}")
            except json.JSONDecodeError:
                print(f"  {line}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
