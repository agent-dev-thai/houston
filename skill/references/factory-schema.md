# Factory Mission Schema

Codex mission files should live under `${CODEX_HOME:-~/.codex}/missions`. Factory missions under `~/.factory/missions` can be imported or mirrored, but should not be the canonical state store for new Codex runs.

Common mission files:

- `working_directory.txt`: absolute repo path for mission matching.
- `state.json`: mission lifecycle state, working directory, update timestamps.
- `mission.md`: product/task objective and milestone overview.
- `architecture.md`: authoritative technical design.
- `AGENTS.md`: mission-specific execution rules.
- `features.json`: feature list with IDs, statuses, milestones, descriptions, preconditions, and validation expectations.
- `validation-contract.md`: assertion-level acceptance criteria.
- `validation-state.json`: recorded assertion state; may be stale.
- `progress_log.jsonl`: event stream for worker starts/completions/pauses/dismissals.
- `handoffs/*.json`: worker handoffs with summaries, changed files, tests, and discovered issues.
- `library/*.md`: detailed environment/testing/domain references.

Status meanings:

- `pending`: intended work not selected by Factory.
- `in_progress`: Factory selected/paused work; inspect logs before resuming.
- `completed`: Factory recorded success; still verify against repo if current state matters.

Reconciliation labels:

- `factory-completed`: Factory recorded completion and repo/tests still support it.
- `implemented-local`: source appears implemented but Factory metadata does not record it.
- `metadata-stale`: Factory status/assertions conflict with repo/test truth.
- `blocked`: required dependency or decision is missing.
- `unknown`: insufficient evidence; inspect more before changing code.
