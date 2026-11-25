---
name: masterskill
description: Use a project development workflow to plan or resume feature implementation, maintain project guidance, and commit completed features.
---

# Masterskill

Apply these rules to the project you are working on. Project paths are relative to its root.

## Decisions and planning

**1. Open questions** — When a decision is unresolved, ask the user and wait for their answer before taking any step that depends on it.

> ✅ The export format is unclear. The agent asks “CSV or XLSX?” and waits for the user’s answer.
>
> ❌ The export format is unclear. The agent picks CSV and starts building.

**2. Write plans and track progress**

Before coding, write the proposed approach and steps in `plans/<plan-name>.md`. Track progress in that plan. Create and maintain `plans/STATE.md` as an index of active, pending, and completed plans. Link to it from `AGENTS.md`. When picking up work, use the index to find the plan that matches the request, verify progress, and continue from there.

> ✅ One agent writes the export plan, marks it active, and records the finished CSV writer. The next agent finds the plan through `STATE.md`, verifies the writer, finishes the tests, and marks the plan complete.
>
> ❌ One agent builds the CSV writer and tracks progress in chat. The next agent starts from scratch and builds the writer again.

**15. Flag issues whenever you find them**

Highlight stale, broken, or partially working items. Report the fix or ask the user for a decision.

> ✅ “MCP was already available. I corrected the outdated guidance in `AGENTS.md`.”
>
> ❌ “`AGENTS.md` still lists MCP as a stretch goal. I left it unchanged.”

## Implementation and workspace hygiene

**3. Follow project coding conventions**

Before coding, read `codestyle/STYLE.md` and follow its guidance for the language and framework in use. If the file or a relevant guide is missing, warn the user and continue.

> ✅ The agent follows the TypeScript guide, warns that the React guide is missing, and continues coding.
>
> ❌ The agent finds the TypeScript guide but stops work because the React guide is missing.

**4. Use project scripts**

Use scripts for repeated file searches, vector generation, resource downloads, dataset or backend changes, and any action that needs testing before live use.

Reuse or create scripts in `scripts/` using a project-appropriate language. List each script’s purpose and run command in `scripts/SCRIPTS.md`. Link the index from `AGENTS.md`.

> ✅ The agent scripts a dataset update, documents it in `SCRIPTS.md`, and tests it on sample data.
>
> ❌ The agent runs the update directly against live data.

**5. Keep working files out of Git**

Store temporary files, large working files, and intermediate outputs in `tmp/`. Add `/tmp/` to `.gitignore` and delete each file when its job is done.

> ✅ The agent extracts an archive into `tmp/`, saves the final output, and deletes the extracted files.
>
> ❌ The agent extracts the same archive into the project root and commits the extracted files.

## Interface copy

**6. Use icons and short labels**

Use icons and short labels. Add text only when it is essential to understand the interface or take an action.

> ✅ The button shows a report icon and the label “Preview.”
>
> ❌ The button says “Preview report” with the subtitle “Text generated, content not human verified, research ongoing.”

## Human and agent documentation

**7. Separate human and agent documentation**

Put human guides directly in `docs/` and agent guides in `docs/agent/`. Link to `docs/agent/` from `AGENTS.md`. Organize each guide by topic, keep it concise, and update the relevant section to match the implementation.

> ✅ For a new CSV export, the agent writes user steps in `docs/export.md` and implementation details in `docs/agent/export.md`.
>
> ❌ The agent appends user steps, backend details, and repeated explanations to `docs/export.md`.

**8. Write the README for people**

Keep `README.md` brief. Explain what the project does, show how to get started, and link to `docs/` for details. In `AGENTS.md`, link to `README.md` and instruct agents to update it whenever implementation changes affect what it says.

> ✅ The install command changes. Following `AGENTS.md`, the agent replaces the old command in the README quick start.
>
> ❌ The install command changes. The agent updates its own setup notes while the README still sends users through the old steps.

**9. Keep agent instructions in one place**

Create `AGENTS.md` and `CLAUDE.md` in the project root. Maintain shared instructions in `AGENTS.md`. Put `@AGENTS.md` in `CLAUDE.md` so Claude loads the current instructions automatically.

> ✅ The agent updates the plan index link in `AGENTS.md`. Claude picks up the new link through `@AGENTS.md`.
>
> ❌ The agent copies the link into both files, then updates only `AGENTS.md` when the index moves.

**14. Fix and report stale documentation**

When you find outdated documentation, verify the current behavior, correct the relevant passage, and tell the user what changed.

> ✅ The guide lists `npm start`. The agent verifies `npm run dev` starts the app, updates the guide, and reports the correction.
>
> ❌ The agent spots the outdated command and tells the user the guide needs an update, leaving `npm start` in place.

**16. Centralize project-specific agent rules**

Keep `docs/agent/rules.md` as the sole source of project-specific rules for agents. Link it from `AGENTS.md` and keep it current. Put implementation details in the relevant `docs/agent/` guide and user instructions in the relevant `docs/` guide.

> ✅ `docs/agent/rules.md` tells agents to pair each new API endpoint with an MCP endpoint. `docs/endpoints.md` shows users how to add endpoints.
>
> ❌ `docs/agent/rules.md` mixes the agent’s MCP requirement with the user’s endpoint setup steps.

## Feature completion and commits

**10. Write single-author commit messages**

Use the bundled [caveman-commit reference](references/caveman-commit.md) to write each commit message. Keep the Git author as the sole author.

> ✅ The agent writes `feat(export): add CSV download` and leaves attribution to Git’s author field.
>
> ❌ The agent writes the same subject and adds a `Co-authored-by` trailer.

**11. Commit completed features**

Keep `.gitignore` current. When a feature is complete, automatically commit only its changes. Follow rule 10 for the commit message and authorship.

> ✅ CSV export is complete. The agent ignores the export cache and commits the feature as `feat(export): add CSV download`, using `caveman-commit` and a single author.
>
> ❌ CSV export is complete. The agent commits the cache with the feature, uses `misc updates` as the message, and adds a `Co-authored-by` trailer.

## Reference material and UI content

**12. Let the project guide the design**

Start with the user’s idea and the role the result serves in the project. Use references for inspiration. Choose content and structure that fit the project as a whole.

> ✅ For a setup screen, the agent borrows a reference’s clear typography and arranges the steps around the app’s setup flow.
>
> ❌ For the same screen, the agent copies the reference’s hero, cards, and testimonials, then fills them with setup instructions.

**13. Keep development conversations out of the UI**

Use the conversation to understand what to build. Write UI copy for the person using the product. Include wording or findings from chat only when the user explicitly asks to display them.

> ✅ After a chat about duplicate uploads, the UI shows “File already uploaded” when someone selects the same file twice.
>
> ❌ The upload screen says “During testing, we found that users sometimes upload the same file twice.”
