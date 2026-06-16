---
name: houston
description: Run, resume, create, import, or reconcile Codex mission-mode coding work using harness-agnostic dynamic workflows. Use when Codex is asked to finish a mission, create a mission for a feature, resume or import a Factory mission, sync mission state with a repo, choose/implement pending feature work from mission files, use fanout/redteam workflows, or translate Claude/Factory workflow primitives into Codex execution.
---

# Houston

Use this skill to turn durable mission files into a live Codex execution loop. The canonical mission home is `$CODEX_HOME/missions` or `~/.codex/missions`; treat `.factory` missions as import sources, not the place to keep new Codex mission state. Always reconcile mission metadata against git status, source files, tests, and validation output.

## Quick Start

1. Locate or create the mission for the current repo.
   - Prefer Codex missions: `scripts/find_mission.py --cwd "$PWD" --latest --missions-root "${CODEX_HOME:-$HOME/.codex}/missions"`.
   - If no Codex mission exists, search `$HOME/.factory/missions` as a legacy import source.
   - Mirror legacy Factory missions with `scripts/import_factory_mission.py <factory-mission-dir>` before continuing when persistent Codex mission state is desired.
   - Create a new Codex-native mission with `scripts/create_mission.py --cwd "$PWD" --title "..." --objective "..."` when the user asks for mission mode on work that has no mission yet.
   - For new work, create the mission under `${CODEX_HOME:-$HOME/.codex}/missions`; do not create or keep new mission state under `.factory`.
   - If multiple missions match, choose the newest by `state.json.updatedAt` after reporting the ambiguity.
2. Read the mission spine:
   - `mission.md`
   - `architecture.md`
   - `features.json`
   - `validation-contract.md`
   - `AGENTS.md`
   - recent `progress_log.jsonl` and `handoffs/*.json`
3. Reconcile current truth.
   - Run `git status --short --branch`.
   - Compare pending/in-progress feature IDs to current diffs, tests, and existing implementation.
   - Report stale Factory metadata explicitly, e.g. "implemented locally, not Factory-certified."
4. Build a live work spine.
   - Use a small task list.
   - Keep one active item.
   - Prefer the mission's `in_progress` feature, then pending features whose preconditions are satisfied.
5. Execute the next coherent slice.
   - Inspect before editing.
   - Keep changes scoped to the feature or reconciled bundle.
   - Validate with mission-specified commands and focused tests.
6. Produce a handoff.
   - Changed files.
   - Feature IDs covered.
   - Validation commands/results.
   - Unresolved assertions, blockers, and Factory metadata drift.

## Dynamic Workflow

Use the Claude-style dynamic loop as the execution shape:

`warm start -> classify -> inspect -> plan spine -> execute -> validate -> repair -> handoff`

Do not hard-code a specific harness. The same workflow must run with Codex tools, Claude Workflow JS, Factory workers, or a sequential fallback. Read `references/dynamic-workflow.md` for the portable loop and `references/harness-agnostic-workflows.md` for adapter rules.

## Fanout And Redteam

Use fanout when the user asks for fanout, subagents, delegation, parallel workers, redteam, or "mission mode with subagents." In Codex, that explicit user request authorizes `multi_agent_v1.spawn_agent` for the current run.

Fanout is especially useful when:

- Multiple legitimate implementations need comparison.
- Independent review can catch subtle bugs.
- Work can be split into disjoint write sets.
- Independent implementation/review/test ownership is possible.

For the reusable fanout-redteam pattern:

1. Implement N candidates in parallel, each in a separate artifact path.
2. Barrier: wait until candidates exist.
3. Redteam agent independently re-derives conventions from source, writes clean-room references/tests, runs all candidates, and selects a survivor.
4. Main agent integrates the survivor and ports the useful tests.

In Codex, when the user explicitly asks for subagents/fanout, spawn at least one subagent unless the task is already complete or spawning is impossible. Without explicit authorization, execute the same phases sequentially.

## Mission State Rules

- Codex mission state belongs under `${CODEX_HOME:-$HOME/.codex}/missions`.
- `.factory` is read/import-only unless the user explicitly asks to update Factory metadata.
- To import a Factory mission, mirror the useful mission spine into a Codex mission directory and record the source path in `state.json` or a short note.
- `features.json` describes intended work and statuses, but source/tests decide current implementation truth.
- `validation-state.json` can be stale. Do not mark assertions as complete unless validation was actually run or the user asks to update Factory metadata.
- `progress_log.jsonl` and `handoffs/` explain history; do not replay old work blindly.
- If external work exists in the repo, map it back to feature IDs before choosing new work.
- Ask before mutating legacy `.factory` files. Normal implementation work belongs in the repo; Codex mission-state mutation belongs in `~/.codex/missions`.

## Scripts

- `scripts/find_mission.py --cwd <repo>` locates matching mission directories; default root is `${CODEX_HOME:-~/.codex}/missions`. Add `--missions-root ~/.factory/missions` to import Factory state. Add `--latest` to print only the newest by `state.json.updatedAt`.
- `scripts/import_factory_mission.py <factory-mission-dir>` mirrors the Factory mission spine into `${CODEX_HOME:-~/.codex}/missions` and records the source Factory path.
- `scripts/create_mission.py --cwd <repo> --title <title> --objective <objective>` creates a small Codex-native mission for new feature work.
- `scripts/summarize_mission.py <mission-dir>` prints feature status counts and recent log tail.

Use scripts for discovery/summary; still read the relevant mission files before editing code.
