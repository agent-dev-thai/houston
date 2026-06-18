---
name: houston
description: Run, resume, create, import, or reconcile Codex mission-mode coding work using harness-agnostic dynamic workflows and subagent-native fanout. Use when Codex is asked to finish a mission, create a mission for a feature, resume or import a Factory mission, sync mission state with a repo, choose/implement pending feature work from mission files, spawn multiple subagents to attack a coding problem, use fanout/redteam workflows, or translate Claude/Factory workflow primitives into Codex execution.
---

# Houston

Use this skill to turn durable mission files into a live Codex execution loop. The canonical mission home is `$CODEX_HOME/missions` or `~/.codex/missions`; treat `.factory` missions as import sources, not the place to keep new Codex mission state. Always reconcile mission metadata against git status, source files, tests, and validation output.

Default to a semantic mission model: understand the goal, split the work into
lanes, delegate independent lanes when subagents are authorized and available,
then integrate from source truth. Do not merely run the next checklist item.

## Quick Start

1. Locate or create the mission for the current repo.
   - Prefer Codex missions: `scripts/find_mission.py --cwd "$PWD" --latest --missions-root "${CODEX_HOME:-$HOME/.codex}/missions"`.
   - If no Codex mission exists, search `$HOME/.factory/missions` as a legacy import source.
   - Mirror legacy Factory missions with `scripts/import_factory_mission.py <factory-mission-dir>` before continuing when persistent Codex mission state is desired.
   - Create a new Codex-native mission with `scripts/create_mission.py --cwd "$PWD" --title "..." --objective "..."` when the user asks for mission mode on work that has no mission yet. Use `--missions-root /tmp/...` for temporary smoke tests or isolated evaluations.
   - For new work, create the mission under `${CODEX_HOME:-$HOME/.codex}/missions`; do not create or keep new mission state under `.factory`.
   - If multiple missions match, choose the newest by `state.json.updatedAt` after reporting the ambiguity.
2. Read the mission spine:
   - `mission.md`
   - `architecture.md` when present
   - `features.json`
   - `validation-contract.md`
   - mission-local `AGENTS.md` when present
   - recent `progress_log.jsonl` and `handoffs/*`
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

## Subagent-Native Mission Workflow

Use fanout when the user asks for fanout, subagents, delegation, parallel
workers, redteam, or "mission mode with subagents." Treat subagents
semantically: use the best available delegation/spawn primitive in the current
harness. Do not name or depend on one specific tool. If no spawn primitive is
available, run the same lane graph sequentially.

Fanout is optional execution strategy, not a default. Use it only when at least
one of these is true:

- Multiple legitimate implementations need comparison.
- Independent review can catch subtle bugs.
- Work can be split into disjoint write sets.
- Independent implementation/review/test ownership is possible.

Do not fan out for one-obvious-fix bugs, tightly coupled edits, unclear write
ownership, secrets/env inspection, or work that requires a live architecture
decision from the main agent. If the user requests fanout anyway, spawn a
reviewer/validator lane or run the lane graph sequentially; do not invent
parallel implementations.

### Lanes

- **Scout:** reads mission/repo context and reports constraints; writes only
  notes/artifacts.
- **Implementation:** owns one isolated source/test slice or candidate artifact
  path.
- **Validator:** owns focused tests, repro scripts, or validation output; avoids
  production source edits unless explicitly assigned.
- **Reviewer/redteam:** independently inspects assumptions, stale paths,
  coupling, spec drift, and candidate quality; recommends, but does not decide.
- **Integrator:** always the main agent. It resolves conflicts, applies final
  source edits, runs checks, repairs, updates mission state, and produces the
  handoff.

Every worker brief must declare: objective, source of truth, lane, allowed write
paths, forbidden write paths/actions, expected artifact, validation command,
expected output, and stop condition.

### Ownership

Give agents disjoint write ownership. No two workers may edit the same real
file, generated file, lockfile, schema, public contract, shared type, or mission
state. Default worker permission is artifact-only. A worker may edit real source
only when assigned an isolated worktree or a disjoint explicit write set. The
main agent owns shared/public surfaces and final integration.

Subagents must not change schemas, auth, money movement, public APIs, generated
ABIs, env files, secrets, or persistent mission state unless that exact surface
is assigned by the main agent and the main agent re-reviews it before
integration.

### Barriers

Use explicit barriers:

1. **Context barrier:** scouts/reviewers finish before implementation when
   constraints are uncertain.
2. **Candidate barrier:** implementation artifacts exist before redteam review.
3. **Validation barrier:** tests/verdicts are complete before integration.
4. **Integration barrier:** main agent ports selected work, removes stale paths,
   validates, and records residual risk.

At each barrier, proceed only with valid artifacts. If a worker stalls or fails,
record the failure and continue with the best available evidence unless the
missing result is required for safety.

For the reusable fanout-redteam pattern:

1. Implement N candidates in parallel, each in a separate artifact path.
2. Barrier: wait until candidates exist.
3. Redteam agent independently re-derives conventions from source, writes
   clean-room references/tests when useful, runs or inspects all candidates, and
   recommends a survivor with evidence.
4. Main agent makes the final integration decision, ports the survivor and
   useful tests, then runs focused validation and mission gates.

Before integration, re-run `git status`, check for user changes, and verify the
selected patch still applies to current source. Do not rely on subagent
validation as final proof.

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
- `scripts/create_mission.py --cwd <repo> --title <title> --objective <objective>` creates a Codex-native mission with mission, architecture, features, validation, AGENTS, state, and progress spine files.
- `scripts/summarize_mission.py <mission-dir>` prints feature status counts and recent log tail.

Use scripts for discovery/summary; still read the relevant mission files before editing code.
