# binloan-masterskill

An agent skill for planning, implementing, and committing features. It keeps progress in the project so another agent can resume the work.

## Install

From the project where you want to use the skill, run:

```sh
npx skills add binloan/binloan-masterskill --skill binloan-masterskill
```

To install from a local checkout, replace `binloan/binloan-masterskill` with the path to that checkout.

## Use

Ask your agent: “Use binloan-masterskill to add CSV export to the reports page.” The agent checks project plans, records progress, and commits the finished feature.

See the [skill instructions](skills/binloan-masterskill/SKILL.md) for the workflow and the [blueprint](BLUEPRINT.md) for the original rules and authoring process.
