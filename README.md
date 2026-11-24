# binloan-masterskill

A development skill for coding agents. It keeps feature plans and progress in your repository so another agent can pick up where the last one stopped.

## Install

Run this in the project where you want to use the skill.

```sh
npx skills add binloan/binloan-masterskill --skill binloan-masterskill
```

To install from a local checkout, replace `binloan/binloan-masterskill` with the path to that checkout.

## Use

> Use binloan-masterskill to add CSV export to the reports page.

The agent records the export plan in `plans/`, tracks its status in `plans/STATE.md`, and follows the project’s coding conventions. When the feature is complete, it commits the feature’s changes automatically.

To resume in a later session, ask the next agent to continue the CSV export plan. It checks the recorded progress against the implementation before picking up the next step.

## Rules

The [skill](skills/binloan-masterskill/SKILL.md) contains 13 rules with examples covering planning, implementation, workspace hygiene, UI design and copy, documentation, and commits. The [blueprint](BLUEPRINT.md) holds approved wording and the review process for proposed changes.
