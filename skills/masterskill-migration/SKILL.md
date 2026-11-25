---
name: masterskill-migration
description: Reorganize an existing project while preserving its behavior, data, and supported workflows. Use for structural changes, including adoption of the Masterskill layout.
---

# Masterskill Migration

## Decisions and planning

**Inspect and plan.** Map what depends on the paths being moved and record which checks pass or fail before editing. Write the proposed layout, stages, checks, and rollback in `plans/<name>.md`. Track progress there and status in `plans/STATE.md`. Verify recorded progress when resuming. Ask the user about unresolved decisions and wait before taking dependent steps. Read the [investigate-first snapshot](references/investigate-first.md) when a dependency or failure is unclear.

## Implementation and verification

**Move in reversible stages.** Follow project conventions and preserve existing work. Update each path with its callers. Keep old entry points working while supported callers still use them. Use tested scripts for bulk moves. Read the [migration snapshot](references/migration.md) when old and new paths must coexist or rollback needs coordination.

**Verify each stage.** Rerun baseline checks and exercise affected entry points before continuing. Record results in the plan. Fix regressions or roll back the stage while preserving the user’s work. Report any checks you couldn’t run.

> ✅ Unit tests pass after a module move. The agent also installs the built package in a clean project and verifies that its public import still works.
>
> ❌ Unit tests pass through a local alias. The agent closes the migration while the published import is broken.

## Documentation and completion

**Update guidance and close the plan.** Fix affected README and docs paths. When adopting the Masterskill layout, link `plans/STATE.md`, `docs/agent/`, and any script index from `AGENTS.md`. Use `@AGENTS.md` in `CLAUDE.md` to load shared guidance. Clean up temporary files, update `.gitignore` as needed, and mark the plan complete after verification. Commit only the migration changes using the [caveman-commit snapshot](references/caveman-commit.md) and a single-author Conventional Commit.
