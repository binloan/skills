# Masterskill

Skills for building features and reorganizing existing projects. Both keep plans and progress in your repository so another agent can pick up where the last one stopped.

## Install

Run the command for the skill you want in your project.

```sh
npx skills add binloan/skills --skill masterskill
npx skills add binloan/skills --skill masterskill-migration
```

To install from a local checkout, replace `binloan/skills` with the path to that checkout.

## Use

### masterskill

> Use masterskill to add CSV export to the reports page.

The agent records the export plan in `plans/`, tracks its status in `plans/STATE.md`, and follows the project’s coding conventions. When the feature is complete, it commits the feature’s changes automatically.

To resume in a later session, ask the next agent to continue the CSV export plan. It checks the recorded progress against the implementation before picking up the next step.

### masterskill-migration

> Use masterskill-migration to move the build scripts into `scripts/` and keep CI working.

The agent maps script callers, records the current checks, and verifies each reversible stage against that baseline.

## Rules

See [masterskill](skills/masterskill/SKILL.md) for the development workflow and [masterskill-migration](skills/masterskill-migration/SKILL.md) for structural migrations. The [blueprint](BLUEPRINT.md) holds the approved rules and review process.
