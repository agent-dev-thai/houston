#!/usr/bin/env python3
"""Create a Codex mission directory for repo-local feature work."""

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


def _write_mission(dest: Path, title: str, objective: str) -> None:
    dest.joinpath("mission.md").write_text(
        f"# {title}\n\n"
        f"## Objective\n\n{objective}\n\n"
        "## Mission Loop\n\n"
        "1. Reconcile mission metadata with git status and source truth.\n"
        "2. Split work into semantic lanes when fanout is useful.\n"
        "3. Keep the main agent as integrator and final validator.\n"
        "4. Record validation and residual risk in the handoff.\n"
    )


def _write_architecture(dest: Path) -> None:
    dest.joinpath("architecture.md").write_text(
        "# Architecture Notes\n\n"
        "## Source Of Truth\n\n"
        "- Repo guidance and project specs\n"
        "- Current git status and source files\n"
        "- Mission features and validation contract\n\n"
        "## Semantic Lanes\n\n"
        "- Scout: inspect constraints and repo context; artifact-only.\n"
        "- Implementation: isolated code/test slice or candidate artifact.\n"
        "- Validator: focused tests, repros, and validation output.\n"
        "- Reviewer/redteam: assumption, coupling, stale-path, and drift review.\n"
        "- Integrator: main agent only; final source edits, validation, handoff.\n\n"
        "## Ownership Rules\n\n"
        "- Give subagents disjoint write sets.\n"
        "- Default subagent permission is artifact-only unless assigned paths.\n"
        "- Main agent owns shared/public surfaces and mission state mutation.\n"
    )


def _write_agents(dest: Path) -> None:
    dest.joinpath("AGENTS.md").write_text(
        "# Mission Agent Instructions\n\n"
        "- Treat mission metadata as stale until reconciled with source and tests.\n"
        "- Use subagents only when the user authorizes fanout/delegation and work "
        "can be split safely.\n"
        "- Every subagent brief must include lane, source of truth, allowed write "
        "paths, forbidden actions, artifact, validation, and stop condition.\n"
        "- Subagents must not edit schemas, auth, money flows, public APIs, env "
        "files, secrets, generated ABIs, or mission state unless explicitly "
        "assigned and reviewed by the main agent.\n"
        "- The main agent is the integrator and final validator.\n"
    )


def _features(title: str, objective: str) -> dict[str, object]:
    feature_id = _slug(title)
    return {
        "features": [
            {
                "id": feature_id,
                "milestone": "implementation",
                "status": "pending",
                "lane": "integrator",
                "owner": "main-agent",
                "description": objective,
                "sourceOfTruth": [
                    "mission.md",
                    "architecture.md",
                    "validation-contract.md",
                    "repo source",
                    "git status",
                ],
                "allowedWritePaths": ["repo task files", "mission handoff files"],
                "forbiddenActions": [
                    "edit env files or secrets",
                    "mutate public contracts without explicit assignment",
                    "claim completion without local validation",
                ],
                "validation": [
                    "feature-specific tests",
                    "mission validation contract",
                    "repo status/diff review",
                ],
            }
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", default=".", help="repo path")
    parser.add_argument("--title", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument(
        "--missions-root",
        default=str(
            Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
            / "missions"
        ),
    )
    args = parser.parse_args()

    now = datetime.now(timezone.utc).isoformat()
    root = Path(args.missions_root).expanduser()
    dest = root / _slug(args.title)
    dest.mkdir(parents=True, exist_ok=True)

    (dest / "working_directory.txt").write_text(
        str(Path(args.cwd).resolve()) + "\n"
    )
    _write_mission(dest, args.title, args.objective)
    _write_architecture(dest)
    _write_agents(dest)
    (dest / "features.json").write_text(
        json.dumps(_features(args.title, args.objective), indent=2) + "\n"
    )
    (dest / "validation-contract.md").write_text(
        "# Validation Contract\n\n"
        "- Feature-specific tests pass.\n"
        "- Focused validation for touched surfaces passes.\n"
        "- Full repo gate passes when practical for the repository.\n"
        "- Handoff records commands, results, blockers, and residual risk.\n"
    )
    (dest / "state.json").write_text(
        json.dumps(
            {
                "missionId": _slug(args.title),
                "state": "active",
                "workingDirectory": str(Path(args.cwd).resolve()),
                "createdAt": now,
                "updatedAt": now,
            },
            indent=2,
        )
        + "\n"
    )
    (dest / "progress_log.jsonl").write_text(
        json.dumps(
            {
                "timestamp": now,
                "type": "codex_mission_created",
                "message": args.objective,
            }
        )
        + "\n"
    )

    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
