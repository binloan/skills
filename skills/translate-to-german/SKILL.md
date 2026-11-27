---
name: translate-to-german
description: Translate a supplied text or file into German with a translator agent and an independent verifier agent, changing only the text. Use for professional or official documents where accuracy, matching tone, consistent terminology, and no invented content matter.
---

# Translate to German

The user supplies text or a file in any source language. A translator agent translates it into German and a verifier agent checks it independently. Return the German text or file with a review. Paths in this file are relative to this skill's folder, except `tmp/`, which is in the user's project. Pass absolute paths to subagents. Use a working Python 3 executable for script commands.

## 1. Prepare

**Read the source first.** Read all of it and name its language. Work in `tmp/translation/<name>/` (git-ignored) and keep an untouched copy of the original there as `source.<ext>`.

**Edit only the text.** Prepare by format:

- `.docx`: run `python scripts/docx_text.py extract source.docx -o segments.json`. It lists every paragraph, table cell, header, footer, footnote, text box, and image description with an ID, a location such as `table 1, row 2, col 2`, and its text. Inside a text, `<t1>…</t1>` marks text with its own formatting, `<o1/>` stands for a non-text item such as a footnote mark, and `<tab/>` and `<br/>` stand for tabs and line breaks.
- `.md`, `.txt`, `.html`: copy to `draft.<ext>` and edit the copy.
- Pasted text: save as `source.txt` and return the result in chat.
- Other formats: stop and tell the user.

If `segments.json` reports tracked changes or comments, tell the user and ask for confirmation to translate the visible text only. Comments and deleted text stay as they are.

For sources over about 10 pages, translate in consecutive batches that end at a heading, never inside a table. Use the same translator for every batch so the glossary carries over, and check each join for repeated headings, restarted numbering, and references across the join.

## 2. Profile

**Profile before translating.** Write `profile.md` in about eight lines: document type, audience, purpose, tone, formality, and address form (Sie or du, as `references/german.md` describes). Take them from cues such as salutation, titles, sentence length, jargon, and who writes to whom. Ask the user once, in one message, about anything the source leaves open and German needs. The user's answer overrides the profile.

> ✅ A letter opens "Dear Mr. Miller" and the profile records formal, Sie, slash forms for gendered terms.
>
> ❌ The agent writes "du" throughout because the English had no distinction.

## 3. Translate

Spawn the translator (Agent tool, a fast model) with the source, `profile.md`, and `references/german.md`, and these rules:

**Keep the document.** Change text only. Add, remove, move, or restyle nothing. Content in a cell stays in that cell, free text stays free text, paragraph order is fixed, and every `<t>`, `<o>`, `<tab/>`, and `<br/>` stays.

> ✅ Three items inside one table cell are still three paragraphs inside that cell.
>
> ❌ The agent lists the items below the table.

**Fix the facts.** Copy names and numbers exactly and change only their written format. Keep claims, references, URLs, code, and template placeholders. If a cited title has no confirmed target-language title, retain the source title and add a gloss where helpful. Add nothing and drop nothing.

> ✅ "Nearly 100 exhibitors" becomes "knapp 100 Aussteller".
>
> ❌ "Nearly 100 exhibitors" becomes "über 500 Aussteller aus 30 Ländern".

**Translate function.** Write each passage as a native German writer would in that situation, taking its meaning and its job from the source and not its words. Idioms, greetings, closings, set phrases, labels, and headings get the wording that fits the profile. Choose the wording yourself, vary it where the text repeats a job, and take no phrase from a list. Reorder, merge, or split sentences inside a paragraph when German needs it.

> ✅ "It's raining cats and dogs" becomes a German sentence that says it is pouring.
>
> ❌ "It's raining cats and dogs" becomes "Es regnet Katzen und Hunde".

**Match the profile.** Keep the source's tone and formality and apply `references/german.md`.

**Mark doubt.** Write `[?]` where the source is unclear or a term is unresolved.

**Research proper nouns.** Look up unfamiliar organisations, products, events, and named people with web search. Record each source URL.

**Log choices.** Write `glossary.md` with a table of terms (source, German, URL or `unverified`) and a table of free renderings (source expression, German, reason).

Output for `.docx`: write `translation.json` as `{"document:1": "German text", …}` with every ID, then run `python scripts/docx_text.py inject source.docx translation.json draft.docx --lang de-DE`. It stops with a message if a tag is missing, so fix the text and run it again. For other formats, write `draft.<ext>`. Then run `python scripts/check_structure.py source.<ext> draft.<ext>` and fix every structure mismatch before handing over.

## 4. Verify

Spawn the verifier (Agent tool, the strongest available model) with the source, draft, `glossary.md`, `profile.md`, and `references/german.md`, and no access to the translator's reasoning. It writes `review.md` (if it cannot write files, save its reply as `review.md`):

- **Both passes.** Source to draft: every source paragraph has a translation. Draft to source: every draft paragraph has a source. Use the script's DOCX segment count if reporting a total.
- **Scripts.** Run `check_structure.py` independently and review the number differences it prints.
- **Meaning and function.** Compare what the text says and does, so a free rendering listed in the glossary passes. In dense formal text, check what each qualifier applies to, whether each part of a paired term survives, and whether quantities written as words retain their value.
- **Terms.** Re-check glossary entries marked `unverified` and any term it doubts. Check the draft against the glossary.
- **Tone.** Check tone and formality against the profile and the decisions in `references/german.md`.
- **Fluency.** Read the German as a native reader would. Report stiff, word-for-word, or repeated phrasing as STYLE.
- **Fabrication signs.** Look for invented specifics, evaluative words, rounded numbers, and extra rows or items.
- **Issue table.** Columns: ID, location, type, source text, draft text, fix.

| Type | Level |
|---|---|
| FABRICATION, OMISSION, STRUCTURE, ACCURACY | must fix |
| TERMINOLOGY, STYLE | should fix |

## 5. Revise

The same translator applies each fix to the affected text and updates any corresponding glossary entries. It settles each `[?]` by choosing wording faithful to the source and logging the decision and any residual ambiguity for the report. Rebuild as in step 3. The verifier rechecks the listed issues and the resolved markers. Run at most one more round, then report what remains.

## 6. Deliver

Name the final file `final.<ext>` and run `python scripts/check_structure.py source.<ext> final.<ext> --final`. Resolve any structural errors or remaining markers before delivery. For a supplied file, copy the checked result next to the original with `-de` added to its name, such as `letter-de.docx`. For pasted text, return the checked translation in chat.

## 7. Review honestly

The verifier returns the report as its reply (a subagent may be blocked from writing it). Save it as `report.md` and show it to the user with the output path. State facts and leave out praise. Mark each claim as checked by script, checked by the verifier, or not checked. Use these sections, in about 25 lines:

- **Verdict.** Ready, ready after the user checks the listed points, or not ready.
- **Checked and not checked.** What the scripts and the verifier covered, and what only a native reader can judge.
- **Fixed.** Issue counts by type.
- **Open points.** A table of location, problem, why it matters, and suggested action. Include any residual ambiguity and every `unverified` term.
- **Judgment calls.** Profile choices (register, address, gendered forms), resolutions of draft markers, and free renderings the user may reverse.
- **Pitfalls.** Text that grew past a fixed-size cell or text box, terms with several accepted translations, ambiguous source passages, content with legal or official weight that needs a qualified reviewer, and warnings from `segments.json` such as fields left as they are.
- **Where to look.** The passages a human should read first, ranked by risk.

> ✅ "Checked by script: table structure. Not checked: whether the clause in section 4 holds under German law."
>
> ❌ "The translation is accurate and ready to use."

Leave the layout as it is. Delete the files in `tmp/translation/<name>/` once the user confirms.
