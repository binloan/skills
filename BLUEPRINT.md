# Binloan Masterskill blueprint

This document is the maintainer’s source of truth for [binloan-masterskill](skills/binloan-masterskill/SKILL.md). Keep it in the repository root, outside the installed skill. The skill should be quick to load and easy to follow.

## Original rules

### Decisions and planning

```text
- do not fill in open questions automatically, come back to the user and ask
- Write steps and implementation into a separete plan which is updateable. have a state document that tells which current plan is active and which were done and which not
```

### Implementation and workspace hygiene

```text
- Always use the related framework and language coding guidelines
- Turn actions into repeatable scripts, do not run bash commands directly but rather make the reproducable and point the agent documentation to it for the future
- put temporary, large or intermedaite files into a special excluded folder or section and clean them once they are not needed anymore
```

### Interface copy

```text
- Prefer icons and labels only, no extra text, no explainers, no prose that isn't absolutely necessary
```

### Human and agent documentation

```text
- build docs both for agents as well as for humans, make sure they are accurate, concise and have a clear structure, do not just append content
- always target the readme to be a human read file. Keep it concise and clear and up to date.
- create an agent.md and a claude.md, make calude always in sny with agent
```

### Feature completion and commits

```text
- use caveman-commit to write commit messages, do not put any co-author
- commit automaticlly once a feature is done, also make sure gitignore is always up to date
```

### Reference material and UI content

```text
- Example documents or files are uniquely meant for inspiration. Direct copy or tight adherence to the files contents must be prevented.
- Leakage of conversation text into UI. Prevent UI elements to contain text or findings from the chat conversation.
```

## Approved skill rules

**1. Open questions** — When a decision is unresolved, ask the user and wait for their answer before taking any step that depends on it.

> [!NOTE]
> ✅ The export format is unclear. The agent asks “CSV or XLSX?” and waits for the user’s answer.
>
> ❌ The export format is unclear. The agent picks CSV and starts building.

**2. Write plans and track progress**

Before coding, write the proposed approach and steps in `plans/<plan-name>.md`. Track progress in that plan. Create and maintain `plans/STATE.md` as an index of active, pending, and completed plans. Link to it from `AGENTS.md`. When picking up work, use the index to find the plan that matches the request, verify progress, and continue from there.

> [!NOTE]
> ✅ One agent writes the export plan, marks it active, and records the finished CSV writer. The next agent finds the plan through `STATE.md`, verifies the writer, finishes the tests, and marks the plan complete.
>
> ❌ One agent builds the CSV writer and tracks progress in chat. The next agent starts from scratch and builds the writer again.

**3. Follow project coding conventions**

Before coding, read `codestyle/STYLE.md` and follow its guidance for the language and framework in use. If the file or a relevant guide is missing, warn the user and continue.

> [!NOTE]
> ✅ The agent follows the TypeScript guide, warns that the React guide is missing, and continues coding.
>
> ❌ The agent finds the TypeScript guide but stops work because the React guide is missing.

**4. Use project scripts**

Use scripts for repeated file searches, vector generation, resource downloads, dataset or backend changes, and any action that needs testing before live use.

Reuse or create scripts in `scripts/` using a project-appropriate language. List each script’s purpose and run command in `scripts/SCRIPTS.md`. Link the index from `AGENTS.md`.

> [!NOTE]
> ✅ The agent scripts a dataset update, documents it in `SCRIPTS.md`, and tests it on sample data.
>
> ❌ The agent runs the update directly against live data.

**5. Keep working files out of Git**

Store temporary files, large working files, and intermediate outputs in `tmp/`. Add `/tmp/` to `.gitignore` and delete each file when its job is done.

> [!NOTE]
> ✅ The agent extracts an archive into `tmp/`, saves the final output, and deletes the extracted files.
>
> ❌ The agent extracts the same archive into the project root and commits the extracted files.

**6. Use icons and short labels**

Use icons and short labels. Add text only when it is essential to understand the interface or take an action.

> [!NOTE]
> ✅ The button shows a report icon and the label “Preview.”
>
> ❌ The button says “Preview report” with the subtitle “Text generated, content not human verified, research ongoing.”

**7. Separate human and agent documentation**

Put human guides directly in `docs/` and agent guides in `docs/agent/`. Link to `docs/agent/` from `AGENTS.md`. Organize each guide by topic, keep it concise, and update the relevant section to match the implementation.

> [!NOTE]
> ✅ For a new CSV export, the agent writes user steps in `docs/export.md` and implementation details in `docs/agent/export.md`.
>
> ❌ The agent appends user steps, backend details, and repeated explanations to `docs/export.md`.

**8. Write the README for people**

Keep `README.md` brief. Explain what the project does, show how to get started, and link to `docs/` for details. In `AGENTS.md`, link to `README.md` and instruct agents to update it whenever implementation changes affect what it says.

> [!NOTE]
> ✅ The install command changes. Following `AGENTS.md`, the agent replaces the old command in the README quick start.
>
> ❌ The install command changes. The agent updates its own setup notes while the README still sends users through the old steps.

**9. Keep agent instructions in one place**

Create `AGENTS.md` and `CLAUDE.md` in the project root. Maintain shared instructions in `AGENTS.md`. Put `@AGENTS.md` in `CLAUDE.md` so Claude loads the current instructions automatically.

> [!NOTE]
> ✅ The agent updates the plan index link in `AGENTS.md`. Claude picks up the new link through `@AGENTS.md`.
>
> ❌ The agent copies the link into both files, then updates only `AGENTS.md` when the index moves.

**10. Write single-author commit messages**

Use the bundled `caveman-commit` reference to write each commit message. Keep the Git author as the sole author.

> [!NOTE]
> ✅ The agent writes `feat(export): add CSV download` and leaves attribution to Git’s author field.
>
> ❌ The agent writes the same subject and adds a `Co-authored-by` trailer.

**11. Commit completed features**

Keep `.gitignore` current. When a feature is complete, automatically commit only its changes. Follow rule 10 for the commit message and authorship.

> [!NOTE]
> ✅ CSV export is complete. The agent ignores the export cache and commits the feature as `feat(export): add CSV download`, using `caveman-commit` and a single author.
>
> ❌ CSV export is complete. The agent commits the cache with the feature, uses `misc updates` as the message, and adds a `Co-authored-by` trailer.

**12. Let the project guide the design**

Start with the user’s idea and the role the result serves in the project. Use references for inspiration. Choose content and structure that fit the project as a whole.

> [!NOTE]
> ✅ For a setup screen, the agent borrows a reference’s clear typography and arranges the steps around the app’s setup flow.
>
> ❌ For the same screen, the agent copies the reference’s hero, cards, and testimonials, then fills them with setup instructions.

**13. Keep development conversations out of the UI**

Use the conversation to understand what to build. Write UI copy for the person using the product. Include wording or findings from chat only when the user explicitly asks to display them.

> [!NOTE]
> ✅ After a chat about duplicate uploads, the UI shows “File already uploaded” when someone selects the same file twice.
>
> ❌ The upload screen says “During testing, we found that users sometimes upload the same file twice.”

## Skill production rules

- Use the category headings and rule order from “Original rules” in the installed skill.
- Record every rule, note, open question, and approved change that affects the skill here before editing the skill. Preserve the original rules above verbatim. When a decision changes, revise the affected guidance in place and identify which original rule it clarifies or supersedes.
- Write short, actionable instructions in `SKILL.md`. Use its description to say when the skill applies. Keep essential rules in the entry point and link supporting material only at the step that needs it.
- Phrase rules positively. Replace each prohibition with a specific action or permitted outcome. Check that the rewrite enforces the same behavior as the original.
- Format each skill rule like rule 1. Give its number and short title, then state the full rule. Follow it with a single GitHub Markdown note callout containing exactly two examples from the same situation, one line each. Start the positive example with ✅ and the negative example with ❌. Describe the agent’s action in plain, direct language.
- Review one rule at a time in chat. Start each review with the original rule verbatim in a code block. Follow it with the proposed rule and both examples. Keep drafts in chat and copy approved wording verbatim into “Approved skill rules.”
- Give each document one job. The editable plan holds implementation steps and progress. The state document points to plans and records their status. Agent guidance identifies applicable coding conventions and repeatable scripts. Human documentation explains how to use the project.
- Keep shared agent instructions in one authoritative place and make the Claude instructions follow it. Apply the preference for icons and labels to interfaces. Use the prose needed to keep instructions and human documentation understandable.
- For commit messages, load the bundled [caveman-commit snapshot](skills/binloan-masterskill/references/caveman-commit.md) on demand and omit co-author trailers. The main skill owns the decision to commit a completed feature. Refresh the snapshot manually.
- Ask the user when an unresolved choice affects behavior. Record the question here and incorporate the answer before generating dependent instructions.
- After each revision, review this document as a whole. Trace each original rule and later decision to the intended behavior, resolve conflicting instructions with the user, and check file roles and links. When producing the skill, repeat that review against the installed files and confirm they work without this blueprint.
