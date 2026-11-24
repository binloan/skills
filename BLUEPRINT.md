# Binloan Masterskill blueprint

This document is the maintainer’s source of truth for [binloan-masterskill](skills/binloan-masterskill/SKILL.md). Keep it in the repository root, outside the installed skill. The skill should be quick to load and easy to follow.

## Original rules

```text
- Always use the related framework and language coding guidelines
- Write steps and implementation into a separete plan which is updateable. have a state document that tells which current plan is active and which were done and which not
- use caveman-commit to write commit messages, do not put any co-author
- create an agent.md and a claude.md, make calude always in sny with agent
- commit automaticlly once a feature is done, also make sure gitignore is always up to date
- always target the readme to be a human read file. Keep it concise and clear and up to date.
- put temporary, large or intermedaite files into a special excluded folder or section and clean them once they are not needed anymore
- build docs both for agents as well as for humans, make sure they are accurate, concise and have a clear structure, do not just append content
- do not fill in open questions automatically, come back to the user and ask
- Prefer icons and labels only, no extra text, no explainers, no prose that isn't absolutely necessary
- Turn actions into repeatable scripts, do not run bash commands directly but rather make the reproducable and point the agent documentation to it for the future
```

## Skill production rules

- Record every rule, note, open question, and approved change that affects the skill here before editing the skill. Preserve the original rules above verbatim. When a decision changes, revise the affected guidance in place and identify which original rule it clarifies or supersedes.
- Write short, actionable instructions in `SKILL.md`. Use its description to say when the skill applies. Keep essential rules in the entry point and link supporting material only at the step that needs it.
- Give each document one job. The editable plan holds implementation steps and progress. The state document points to plans and records their status. Agent guidance identifies applicable coding conventions and repeatable scripts. Human documentation explains how to use the project.
- Keep shared agent instructions in one authoritative place and make the Claude instructions follow it. Apply the preference for icons and labels to interfaces. Use the prose needed to keep instructions and human documentation understandable.
- For commit messages, load the bundled [caveman-commit snapshot](skills/binloan-masterskill/references/caveman-commit.md) on demand and omit co-author trailers. The main skill owns the decision to commit a completed feature. Refresh the snapshot manually.
- Ask the user when an unresolved choice affects behavior. Record the question here and incorporate the answer before generating dependent instructions.
- After each revision, review this document as a whole. Trace each original rule and later decision to the intended behavior, resolve conflicting instructions with the user, and check file roles and links. When producing the skill, repeat that review against the installed files and confirm they work without this blueprint.
