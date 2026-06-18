# Dynamic Workflow Reference

This is the harness-agnostic workflow shape inspired by Claude Code dynamic workflows.

## Loop

1. **Warm start**
   - Read durable context: mission files, repo guidance, recent handoffs, progress logs.
   - Treat cached state as useful but stale until verified.

2. **Classify**
   - Decide whether the current turn is exploration, implementation, validation, repair, or handoff.
   - Select the smallest workflow that can finish the requested outcome.

3. **Inspect**
   - Read code, tests, configs, schemas, and mission contracts before editing.
   - Prefer discovered facts over user questions when the environment can answer.

4. **Plan spine**
   - Maintain a short live task list.
   - Keep exactly one active item.
   - For fanout, convert the plan into semantic lanes with disjoint write ownership and explicit barrier points.
   - Revise the list when validation or repo facts change the path.

5. **Execute**
   - Implement the smallest coherent slice.
   - Keep ownership boundaries clear.
   - When using subagents, keep the main agent as integrator and final validator.
   - Avoid unrelated refactors.

6. **Validate**
   - Run focused tests first, then broader mission gates.
   - Capture exact commands and results.
   - Treat failed validation as input to the next repair loop.

7. **Repair**
   - Diagnose from failure output.
   - Patch narrowly.
   - Re-run the failing validation before broad tests.

8. **Handoff**
   - Map work to mission feature IDs and validation assertions.
   - List changed files and commands run.
   - Record blockers, residual risk, and stale metadata.

## Decision Rules

- Live repo state beats mission metadata when they disagree.
- Tests passing beats inferred completion, but only for the behavior the tests actually cover.
- A feature can be "implemented locally" and still "not Factory-certified."
- Do not mutate persistent mission state unless asked.
