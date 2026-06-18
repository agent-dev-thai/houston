# Harness-Agnostic Workflows

Define workflows as portable intent, then adapt them to the available runtime.

## Portable Workflow Contract

A workflow is portable when it declares:

- `goal`: the user-facing objective.
- `source_of_truth`: files or systems to read before acting.
- `phase_graph`: ordered or parallel phases and barrier points.
- `roles`: implementer, reviewer, redteam, validator, integrator.
- `lanes`: semantic work lanes that can run in parallel or sequentially.
- `ownership`: allowed and forbidden write paths/actions for each lane.
- `artifacts`: expected files, test outputs, verdicts, and handoffs.
- `validation`: commands or checks that prove completion.
- `integration_owner`: who is allowed to touch real source files.
- `fallback`: how to run without subagents or workflow tools.

## Adapter Rules

### Codex

- Use native tools and `update_plan` for the live spine.
- Use the available subagent/delegation primitive only after the user explicitly authorizes subagents/fanout.
- If fanout is authorized, delegate at least one independent implementation, review, test, or reconciliation lane unless the task is already complete, tightly coupled, unsafe to split, or spawning is unavailable.
- Give workers disjoint ownership when editing.
- Main agent integrates and validates.

### Claude Workflow JS

- Express phases with `phase()`, `parallel()`, and `agent()` when that harness exists.
- Require structured outputs for candidate/verdict artifacts.
- Keep integration outside the workflow when real source edits need judgment.

### Factory

- Treat Factory as a legacy/import harness when running this Codex skill.
- Map phases to feature IDs when possible.
- Use `features.json` for status/preconditions.
- Use `progress_log.jsonl` and `handoffs/` for history.
- Run mission validators before claiming Factory-level completion.

### Sequential Fallback

- Run the same phase graph serially.
- Create the same artifacts.
- Make the handoff explicit that no fanout occurred.

## Fanout-Redteam Pattern

Use when a spec has multiple plausible valid algorithms or implementation strategies.

1. **Implement:** produce N candidates, each in its own file or isolated write set.
2. **Barrier:** wait for every candidate artifact.
3. **Redteam:** independently re-read source conventions, write clean-room references/tests when useful, run or inspect every candidate, and recommend a survivor with evidence.
4. **Integrate:** main agent chooses, ports the survivor and useful tests into the repo, and reruns validation.

Do not use this pattern for ordinary CRUD changes, one-obvious-fix bugs, or tightly coupled edits.
