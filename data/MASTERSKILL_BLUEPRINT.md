# Masterskill blueprint

This document is the maintainer’s source of truth for [masterskill](../skills/masterskill/SKILL.md) and [masterskill-migration](../skills/masterskill-migration/SKILL.md). Keep it in the repository root, outside the installed skills. Keep each skill quick to load and easy to follow.

## Original rules

*All submitted rules are approved.*

## Approved skill rules

### Project startup

**1. Load Masterskill first**

The first time you use `masterskill` in a project, put this instruction at the top of the root `AGENTS.md`. Create the file if needed.

> At the start of every agent session in this project, load `masterskill` before any other skill.

> [!NOTE]
> ✅ Adds the instruction to `AGENTS.md`. The next session loads `masterskill` first.
>
> ❌ Adds the instruction to the current plan. The next session starts without loading `masterskill`.

### Decisions and planning

**18. Open questions** — When a decision is unresolved, ask the user and wait for their answer before taking any step that depends on it.

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

**15. Flag issues whenever you find them**

Highlight stale, broken, or partially working items. Report the fix or ask the user for a decision.

> [!NOTE]
> ✅ “MCP was already available. I corrected the outdated guidance in `AGENTS.md`.”
>
> ❌ “`AGENTS.md` still lists MCP as a stretch goal. I left it unchanged.”

### Implementation and workspace hygiene

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

**17. Track external sources**

For every external file or dataset you download and use, save the download in `tmp/`. In `docs/data/SOURCES.md`, record where you got it and what you used it for. Update the entry if either changes.

> [!NOTE]
> ✅ Saves the CSV in `tmp/` and records its URL and “used to calculate monthly sales totals.”
>
> ❌ Uses the CSV to calculate monthly sales totals and leaves it out of the source list.

### Interface copy

**6. Use icons and short labels**

Use icons and short labels. Add text only when it is essential to understand the interface or take an action.

> [!NOTE]
> ✅ The button shows a report icon and the label “Preview.”
>
> ❌ The button says “Preview report” with the subtitle “Text generated, content not human verified, research ongoing.”

### Human and agent documentation

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

**14. Fix and report stale documentation**

When you find outdated documentation, verify the current behavior, correct the relevant passage, and tell the user what changed.

> [!NOTE]
> ✅ The guide lists `npm start`. The agent verifies `npm run dev` starts the app, updates the guide, and reports the correction.
>
> ❌ The agent spots the outdated command and tells the user the guide needs an update, leaving `npm start` in place.

**16. Centralize project-specific agent rules**

Keep `docs/agent/rules.md` as the sole source of project-specific rules for agents. Link it from `AGENTS.md` and keep it current. Put implementation details in the relevant `docs/agent/` guide and user instructions in the relevant `docs/` guide.

> [!NOTE]
> ✅ `docs/agent/rules.md` tells agents to pair each new API endpoint with an MCP endpoint. `docs/endpoints.md` shows users how to add endpoints.
>
> ❌ `docs/agent/rules.md` mixes the agent’s MCP requirement with the user’s endpoint setup steps.

### Feature completion and commits

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

### Reference material and UI content

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

## Approved masterskill-migration rules

Reorganize an existing project while preserving its behavior, data, and supported workflows. Use for structural changes, including adoption of the Masterskill layout.

### Decisions and planning

**1. Inspect and plan.** Map what depends on the paths being moved and record which checks pass or fail before editing. Write the proposed layout, stages, checks, and rollback in `plans/<name>.md`. Track progress there and status in `plans/STATE.md`. Verify recorded progress when resuming. Ask the user about unresolved decisions and wait before taking dependent steps. Read the [investigate-first snapshot](../skills/masterskill-migration/references/investigate-first.md) when a dependency or failure is unclear.

### Implementation and verification

**2. Move in reversible stages.** Follow project conventions and preserve existing work. Update each path with its callers. Keep old entry points working while supported callers still use them. Use tested scripts for bulk moves. Read the [migration snapshot](../skills/masterskill-migration/references/migration.md) when old and new paths must coexist or rollback needs coordination.

**3. Verify each stage.** Rerun baseline checks and exercise affected entry points before continuing. Record results in the plan. Fix regressions or roll back the stage while preserving the user’s work. Report any checks you couldn’t run.

> ✅ Unit tests pass after a module move. The agent also installs the built package in a clean project and verifies that its public import still works.
>
> ❌ Unit tests pass through a local alias. The agent closes the migration while the published import is broken.

### Documentation and completion

**4. Update guidance and close the plan.** Fix affected README and docs paths. When adopting the Masterskill layout, link `plans/STATE.md`, `docs/agent/`, and any script index from `AGENTS.md`. Use `@AGENTS.md` in `CLAUDE.md` to load shared guidance. Clean up temporary files, update `.gitignore` as needed, and mark the plan complete after verification. Commit only the migration changes using the [caveman-commit snapshot](../skills/masterskill-migration/references/caveman-commit.md) and a single-author Conventional Commit.

## Skill production rules

- Use the category headings and rule order from each skill’s approved rules in its installed entry point.
- Record every rule, note, open question, and approved change that affects the skill here before editing the skill. Keep submitted wording verbatim in “Original rules” while it awaits approval. When a decision changes, revise the affected guidance in place.
- Write short, actionable instructions in `SKILL.md`. Use its description to say when the skill applies. Keep essential rules in the entry point and link supporting material only at the step that needs it.
- Phrase rules positively. Replace each prohibition with a specific action or permitted outcome. Check that the rewrite enforces the same behavior as the original.
- Give each rule a number and short title, then state the full rule. Include an example pair for every `masterskill` rule and where it clarifies a practical distinction in `masterskill-migration`. Use a blockquote with one line per example from the same situation. Start the positive example with ✅ and the negative example with ❌. Describe the agent’s action in plain, direct language.
- Treat a request to add or change rules as the start of a review. Review each rule individually with the user in chat. Show the original rule verbatim in a code block, followed by the proposed wording, both examples, and the proposed category. Use an existing category when it fits and propose a new category when needed. Ask the user to explicitly approve the wording, examples, and category. Wait for approval before editing the approved rules or skill files for that rule or presenting the next rule. If the user requests changes, show the revised proposal and wait for approval again. Keep drafts in chat and the original submission in “Original rules” while review is pending.
- After the user explicitly approves a proposal, record its approved wording and examples under the approved category. Add the category heading to the blueprint and affected skill if it is new. Remove the original from “Original rules” in the same edit and update the affected skill with the approved wording and examples under that category.
- Give each document one job. The editable plan holds implementation steps and progress. The state document points to plans and records their status. Agent guidance identifies applicable coding conventions and repeatable scripts. Human documentation explains how to use the project.
- Keep shared agent instructions in one authoritative place and make the Claude instructions follow it. Apply the preference for icons and labels to interfaces. Use the prose needed to keep instructions and human documentation understandable.
- For commit messages, load the bundled [caveman-commit snapshot](../skills/masterskill/references/caveman-commit.md) on demand and omit co-author trailers. The main skill owns the decision to commit a completed feature. Refresh the snapshot manually.
- Keep `masterskill-migration` independently installable with its own reference snapshots. The investigate-first and migration snapshots come from Caveman revision [`47c61be`](https://github.com/JuliusBrussee/caveman/tree/47c61be2d10a354f0c5cbe2b90959d24c06b16c6). Refresh snapshots manually and keep the upstream license and notice with them.
- Ask the user when an unresolved choice affects behavior. Record the question here and incorporate the answer before generating dependent instructions.
- After each revision, review this document as a whole. Trace each approved rule and later decision to the intended behavior, resolve conflicting instructions with the user, and check file roles and links. When producing the skill, repeat that review against the installed files and confirm they work without this blueprint.
