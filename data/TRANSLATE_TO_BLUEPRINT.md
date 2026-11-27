# translate-to blueprint

This document is the maintainer's source of truth for the `translate-to-<target>` skills. It tells an agent how to turn the upstream skill into a family of per-target-language skills. Keep it outside the installed skills. Follow the [Skill production rules](MASTERSKILL_BLUEPRINT.md#skill-production-rules) for wording, rule titles, and review with the user.

## Source

| Item | Value |
|---|---|
| Upstream | [senshinji/claude-translation-skill](https://github.com/senshinji/claude-translation-skill), MIT licence |
| Local copy | `data/claude-translation-skill/`, a git submodule pinned at `42d6c8a` |
| Role | Read-only input. Edit only the new skills. Refresh the pin manually. |
| Used for | Source for the transformation below. Nothing is installed from it. |

Upstream is about 67 KB across 6 reference files, 2 test scripts, and a 494-line `SKILL.md` that needs the experimental Agent Teams flag. The goal is one entry point of roughly 120 lines plus one language file.

## How the skill is used

The user invokes `translate-to-german` and supplies a source: pasted text or a file. The skill fixes the target language. The source language is detected. Pasted text is treated as a `.txt` source and the translation is returned in chat.

## Goals

**Keep**
- Two agents: one translates, one independently verifies.
- Source format handling, so the translator sees tables and structure.
- No invented, dropped, or altered facts.
- Web lookup for proper nouns, recorded with its source.

**Change**
- **Transparent translation.** The delivered file equals the source except for its text. Layout, styles, tables, images, and metadata stay as they are.
- **Idiomatic freedom where content calls for it.** The translator writes as a native writer would and takes no wording from a phrase list. Facts and structure stay fixed.
- **Tone and formality follow the source.** The skill profiles the source before translating.
- One skill per target language, with that language's quirks in one file.
- Plain subagents. Remove Agent Teams, team lead, and term-researcher agents.
- One definition per rule. Upstream states structure rules in six places and anti-fabrication rules in three.
- Scripts check what can be checked by counting and comparing, so the agents judge only meaning.
- **Honest final review.** The user receives a short report of what was checked, what was not, and where a human should look.

## Decisions

| # | Question | Answer |
|---|---|---|
| 1 | Which language is fixed? | The target. The skill names it, the user supplies the source. |
| 2 | First skill | `translate-to-german`. The user verifies German. |
| 3 | Typesetting | Dropped. Return the source's own format with only the text changed. |
| 4 | Chunking | Chunks are translated in order by the same translator so the glossary carries over. |
| 5 | Naming | `translate-to-<target>`, in English lowercase. |
| 6 | Editing `.docx` | Extract, translate, and inject segments with `skills/translate-to-german/scripts/docx_text.py`. Human-text runs passed final structure checks. Visual rendering in Word and LibreOffice remains open. |
| 7 | German variant | de-DE with `ß`. |
| 8 | Address | Formal register uses Sie. Informal register uses du. The profile decides which, and asks when the source gives no cue. |
| 9 | Gendered terms | All formal-register text, including letters, reports, and contracts, uses the slash form with hyphen, such as `Mitarbeiter/-innen`. Informal register keeps the generic masculine. |
| 10 | Tracked changes and comments in `.docx` | Translate only the visible text. Before translating, tell the user that revision marks or comments exist and ask for confirmation. Leave comments and deleted text unchanged. |
| 11 | Formats | `.docx`, `.html`, `.md`, `.txt` first. `.pptx` and `.xlsx` follow with the same segment method once `.docx` works. Other formats stop and tell the user. |
| 12 | Final review | The skill ends with an honest review for the user, with the translation's limits and pitfalls. |
| 13 | `du` | Lower case, in letters too. |
| 14 | Edge cases of the slash form | Stem changes (`Ärzte/-innen`) and article pairs (`der/die Kunde/Kundin`) take the generic masculine. |
| 15 | Instructions | Imperative or infinitive follows the form of the source text. It is not a general rule. |
| 16 | Currency | Keep the source's symbol or code and convert nothing. |
| 17 | VAT | The translator picks by context: `MwSt.` in everyday text, `USt.` in business and tax text. |
| 18 | Section numbering | Stays as in the source. The layout does not change. |

### Test material

**Human text only.** Test texts are written by people. AI-written text makes the translator sound stiff and robotic, which is what the skill must avoid, so no test text, reference translation, or example is generated.

**Keep test material local.** Store test texts, reference translations, and fixture scripts under the Git-ignored `data/translation-test-texts/` and `data/translation-test-scripts/` directories. Store generated run artifacts under the Git-ignored `tmp/translation/` directory.

**Keep benchmark runs blind.** Give the translator and verifier the source-language fixture and their workflow inputs. Hold back the published target-language reference until the final independent recheck is complete. For terminology, open direct links to separate publications that cannot expose the benchmark passage. Record accidental exposure, including search snippets, and rerun the affected stage with a fresh agent before counting the result as blind.

- **Pairs.** Name fixtures `<name>_<lang>.docx`, using the same fixture ID and an uppercase two-letter language code for each version. Record sources, licences, and known differences in the local `data/translation-test-texts/SOURCES.md`.
- **Text1.** Short informal EN–DE pair with 21 source segments.
- **Text2.** Two informal EN–DE excerpts. The local `make_text2_excerpts.py` script (requires `pypdf`) builds them from PDF fixtures. Compare fluency and register, accounting for differences in wording and paragraphing.
- **Text3.** One EN source and two DE references for the `du` and `Sie` register variants.
- **Text4.** Long formal EN–DE pair for testing chunking. A shorter run may use selected sections.
- **Text5 and Text6.** Formal and informal KO–DE pairs, respectively.
- **Text7 and Text8.** Formal and informal ZH–DE pairs, respectively.
- **Error variants.** `data/translation-test-scripts/german/make_error_texts.py` makes `<name>-errors_DE.docx` from the human German and copies the English to `<name>-errors_EN.docx`. Every error is a mechanical edit of the human text: a word swap, a deleted sentence, a sentence copied from elsewhere in the same text, or a removed paragraph style. Nothing is written for the test.
- **Key.** `<name>-errors-key.md` lists each error, its type, and its edit. It sits in the scripts folder so the verifier never sees it. `Text1-errors` carries 10 errors: 4 ACCURACY, 2 OMISSION, 1 FABRICATION, 1 TERMINOLOGY, 1 STYLE, 1 STRUCTURE.
- **Scripts.** The local `data/translation-test-scripts/german/` directory holds `make_error_texts.py` and `roundtrip_test.py` (extract and inject on any `.docx`, with and without rebuilding every paragraph).

### Status

| Check | Result |
|---|---|
| `docx_text.py` round trip on the four human `.docx` files | Passed. 84 segments, no failures. |
| Error variant differs from the human German only where the key says | Passed. Nine text edits and one style removal. |
| `check_structure.py` on an error variant | Reports the STRUCTURE error. The two human files also differ in auto-generated bookmark names, which the key explains. |
| Human-text workflow | Text1, both Text2 excerpts, Text3, and Text5–Text8 completed revision, verification, and delivery. All final DOCX files passed the structure, segment ID, and unresolved-marker checks. The two Text5 number warnings were checked against the source dates. |
| Verifier on `Text1-errors` against the key | A verifier with no access to the key found all 10 seeded issues, plus issues in the human candidate and a pre-existing bookmark difference. |
| Word and LibreOffice opening the output | **Not tested.** Neither is installed here. |
| Other formats and source languages | A French `.txt` passed the translation and delivery smoke test. Sample `.md` and `.html` passed final script checks. Sources over 10 pages still need a workflow test. |
| DOCX regression checks | All 22 local fixture files passed the round-trip test. Targeted checks covered missing and blank alt text, XML escaping, and rejection of unresolved final markers. |

Fixes that came out of the discarded run stay in the scripts: `check_structure.py` ignores the deliberate language change and compares paragraph styles and table cell merges, and the verifier returns its report as text because a subagent may be blocked from writing it.

Known limits of `docx_text.py`:
- Text inside fields (table of contents, cross-references) is kept as is and reported as a warning.
- The `mc:Fallback` copy of a text box, read only by Word 2007 and older, is kept as is and reported.
- Comments and deleted text are not touched, as decided.
- Rebuilt runs lose `rsid` attributes. Splitting a tracked insertion or hyperlink into two clones repeats its attributes.
- A translation that drops a formatting tag is rejected. Dropping bold from a word on purpose needs the tag kept.

### Open questions

Ask the user and record each answer here before generating dependent instructions. Proposed defaults are in bold.

- **`references/german.md` is AI-drafted.** A phrase list makes the translator reuse those phrases and read stiffly. The list is removed. Default: **the file keeps conventions only (register, formats, punctuation, false friends) and, once more texts exist, takes its guidance from them.** All `[?]` items are settled (decisions 13 to 18). The rest of the file is still my draft from memory and needs the user's review.
- **Real Word test.** Open an output file in Word. Default: **no fallback is needed unless Word reports a problem.**
- **PPTX and XLSX details.** Overflow in fixed-size text boxes, slide notes, shared strings, and sheet names used in formulas. Settle them when the formats are added.

## Disposition of upstream content

| Upstream | Action | Result |
|---|---|---|
| `SKILL.md` description, Chinese trigger words | Rewrite | Two sentences naming the target language and when to use the skill |
| Architecture diagram, Prerequisites | Drop | Plain subagents need no flag |
| Phase 0.1 source reading and format handling | Keep, change | Step 1. Keep the insight that the translator must see tables. Replace conversion with in-place extraction. |
| Chunking (Phase 0.1, 3.5, `scaling-guidelines.md`) | Merge | One short chunking paragraph with a seam check |
| Structure manifest, structure report, reviewer comparison table | Replace | `check_structure.py` output |
| Workspace paths, three contracts | Reduce | Files in `tmp/translation/<name>/` |
| `glossary-schema.md`, JSON glossary, confidence scores, timing metadata | Replace | `glossary.md` tables |
| `term-researcher`, fast/deep split, Phase 1.5 merge | Drop | Translator researches. Verifier re-checks. |
| Translator prompt | Keep, shorten | Structure and no-fabrication rules, stated once |
| Reviewer prompt, `review-feedback-schema.md` | Merge | One verifier step with one issue table |
| `anti-fabrication-checklist.md` | Merge | Forward and backward pass plus red flags, in five lines |
| Phase 4.1 lead validation | Replace | Verifier re-checks its own issues, then writes the final review |
| Phase 4.2-4.3, `typesetting-rules.md` | Drop | Decision 3 |
| Test scripts, CI | Replace | Keep the counting logic inside `check_structure.py`. Drop the grep tests, which check wording and not behaviour. |
| README | Drop | Add an entry to this repo's README |

## Defects to resolve in the rewrite

| Upstream defect | Resolution |
|---|---|
| Severity contradicts priority. The contract ranks STRUCTURE fifth, the schema calls it Critical, and the reviewer checks it second. | One table: FABRICATION, OMISSION, STRUCTURE, ACCURACY are must-fix. TERMINOLOGY and STYLE are should-fix. |
| First pass is `.md`, yet the rules require merged cells and multi-item cells with `<br>`. Markdown cannot hold them. | Edit the source's own format. Text formats are edited directly. `.docx` goes through segments. |
| Translators start before the glossary exists, chunk translators "read it when available", and revision then rewrites terms. | The translator builds `glossary.md` as it translates. The verifier checks it. No second terminology pass. |
| Chunked runs write `first-pass-chunk-N.md` while the translator "owns first-pass.md". The reviewer reads `structure-report.md`, which becomes per-chunk. | Fixed file names per run. Chunks are merged before verification. |
| Review results travel by file and by message. | Files only. |
| Models are named in both the lead's table and the spawn prompts. | Set the model once at spawn. Translator: fast model. Verifier: strongest available. No model IDs in the skill. |
| `[?原文?]` and `[unclear in original]` markers have no exit rule and can reach the final file. | Marker is `[?]`. Resolve it or list it in the final report. The final file contains none. |
| `textutil` exists only on macOS. `/tmp/...` paths fail on Windows. | Cross-platform Python scripts. Workspace is `tmp/translation/` in the project, git-ignored. |
| Pinyin, venue names, and `一、` numbering are baked into a nominally generic skill. | Move source-language notes into the language file. |
| Real-failure anecdotes ("13 structure failures") are embedded in prompts. | Keep the rule and one ✅/❌ pair. Drop the history. |
| Prompts reference sibling skills `translation-layout` and `formal-doc-layout`. | Remove. The skill is self-contained. |
| Reviewer compares words, so a correct idiomatic rendering reads as an error. | ACCURACY compares meaning and function. The glossary logs free renderings so the verifier can judge them. |

## Target skill

Build `skills/translate-to-german/` first, in the same layout as the other skills. Each later language is a copy of that folder with its own name, description, and language file. Add a generator only if copies start to drift.

```
SKILL.md
references/german.md                     hand-written language file
references/translation-quality.LICENSE   copy of upstream LICENSE
references/translation-quality.NOTICE    upstream URL and revision, as in the masterskill snapshots
scripts/docx_text.py
scripts/check_structure.py
```

### SKILL.md

Frontmatter: `name: translate-to-<target>`. Description in two sentences: translate a supplied text or file into the target language with a translator and an independent verifier, changing only the text; use for professional or official documents where accuracy, matching tone, consistent terminology, and no invented content matter.

Body, with rules titled and phrased positively, at most 120 lines:

1. **Prepare.** Read the whole source. Name the source language. Work in `tmp/translation/<name>/` and keep an untouched copy of the original.
   - `.html`, `.md`, `.txt`: edit a copy directly.
   - `.docx`: if the file has tracked changes or comments, tell the user and ask for confirmation to translate the visible text only. Then run `docx_text.py extract`. Each segment carries an ID and a location label such as `table 2, row 3, col 1` or `heading 2`, so the translator reads tables as tables.
   - Pasted text: save as `source.txt` and return the checked translation in chat.
   - Other formats: stop and tell the user.
   - Over about 10 pages: split at top-level headings, outside any table, and translate chunks in order with the same translator. Check each join for repeated headings, restarted numbering, and references that point across the join.
2. **Profile.** Before translating, write `profile.md` in about eight lines: document type, audience, purpose, tone, formality, address form, and the source's own house conventions. Take these from cues such as salutations, titles, sentence length, jargon, and who writes to whom. Ask the user once, in one message, about anything the source leaves open and the target needs, for example English "you" becoming Sie or du. The user's answer overrides the profile.
3. **Translate.** Spawn the translator with the source, `profile.md`, and `references/<target>.md`. Give it these rules:
   - **Keep the document.** Change text only. Add, remove, move, or restyle nothing. Content in a cell stays in that cell, free text stays free text, and paragraph order is fixed.
   - **Fix the facts.** Copy names and numbers exactly, and localise only their written format. Keep claims, references, URLs, and code as they are.
   - **Translate function.** Write each passage as a native writer would in that situation, taking its meaning and its job from the source and not its words. Idioms, greetings, closings, set phrases, labels, and headings get the wording that fits the profile. Choose the wording yourself, vary it where the text repeats a job, and take no phrase from a list. Reorder, merge, or split sentences inside a paragraph when the target needs it.
   - **Match the profile.** Keep the source's tone and formality, and apply the language file.
   - **Mark doubt.** Write `[?]` where the source is unclear or a term is unresolved.
   - **Research proper nouns.** Look up unfamiliar organisations, products, events, and named people. Transliterate names that have no translation. Record each source URL.
   - **Log choices.** In `glossary.md`, keep a term table (source, translation, URL or `unverified`) and a short table of free renderings (source expression, translation, reason).
   - Write the draft, run `check_structure.py`, and fix every mismatch before handing over.
4. **Verify.** Spawn the verifier with the source, draft, glossary, profile, and language file. It writes `review.md`:
   - Backward pass, source to draft: every source paragraph has a translation. Forward pass, draft to source: every draft paragraph has a source.
   - Run `check_structure.py` independently. Review the number differences it prints.
   - Compare meaning and function, so an idiomatic rendering listed in the glossary passes.
   - Re-check glossary entries marked `unverified` and any term it doubts. Check the draft against the glossary.
   - Check tone and formality against the profile, and the language file's checklist.
   - Watch for fabrication signs: invented specifics, evaluative words, rounded numbers, extra rows or items.
   - List issues as a table: ID, location, type, source text, draft text, fix.

   | Type | Level |
   |---|---|
   | FABRICATION, OMISSION, STRUCTURE, ACCURACY | must fix |
   | TERMINOLOGY, STYLE | should fix |
5. **Revise.** The same translator applies the fixes to the affected text, updates the glossary, and records how each `[?]` was resolved. The verifier rechecks the listed issues and resolved markers. Run at most one more round, then report what remains.
6. **Deliver.** For `.docx`, use `docx_text.py inject` to rebuild the file and set its language. Run `check_structure.py SOURCE FINAL --final` before delivering.
7. **Review honestly.** The verifier writes `report.md` for the user and the main agent shows it with the output path. State facts and leave out praise. Label each claim as checked by script, checked by the verifier, or not checked. Use these sections, in about 25 lines:
   - **Verdict.** One of: ready, ready after the user checks the listed points, or not ready.
   - **Checked and not checked.** What the scripts and the verifier covered, and what only a native reader can judge.
   - **Fixed.** Issue counts by type.
   - **Open points.** A table: location, problem, why it matters, and suggested action. Include residual ambiguity and every `unverified` term.
   - **Judgment calls.** Profile choices (register, address, gendered forms), resolutions of draft markers, and free renderings the user may want to reverse.
   - **Pitfalls.** Text that grew past a fixed-size cell or text box, terms with several accepted translations, source passages that were ambiguous, content with legal or official weight that needs a qualified human reviewer, and anything the extraction could not carry.
   - **Where to look.** The passages a human should read first, ranked by risk.

   Leave the layout as it is. Delete the working files once the user confirms.

Give ✅/❌ pairs for the keep-the-document rule (a multi-item cell stays one cell), the fix-the-facts rule ("nearly 100" stays "nearly 100"), the translate-function rule (an idiom becomes a sentence that does the same job, not a word-for-word copy), and the review rule ("Checked by script: table structure. Not checked: whether the legal clause in section 4 holds under German law." against "The translation is accurate and ready to use.").

### docx_text.py

Python 3 standard library only. It splices changed paragraphs into the raw XML, so every other byte of the file stays as it was.

- `extract SOURCE -o segments.json` writes one segment per paragraph and per image alt text, covering body, tables, headers, footers, footnotes, endnotes, and text boxes. Each segment has an ID, a location label such as `table 1, row 2, col 2`, and its text. The file also reports tracked changes, comments, and warnings.
- Segment text carries three kinds of markup, which the SKILL.md translator rules must state: `<t1>..</t1>` marks text with its own formatting and appears only when a paragraph has more than one, `<o1/>` stands for a non-text item such as a footnote mark, and `<tab/>` and `<br/>` stand for tabs and line breaks. The translator keeps every tag and moves tags with the words.
- `inject SOURCE translation.json OUT --lang de-DE` takes a plain `{"id": "text"}` map and writes the translation back and sets the document language. It fails on a missing or unknown ID or a broken tag, and writes nothing.

### check_structure.py

Python 3 standard library only. Usage: `python check_structure.py <source> <draft> [--final]`.

- **Skeleton check.** Remove the text from both files and require that what remains is identical: tags and attributes for HTML (except `alt`, `title`, `lang`), syntax markers for Markdown, line and paragraph structure for text, and the XML tree outside text nodes for `.docx`. Print one line per mismatch, with its location.
- **Numbers.** Compare digit sequences with grouping and decimal separators removed, so `1,200` and `1.200` match. Print each difference and leave the judgement to the verifier.
- Report DOCX segment counts. Exit 1 on a skeleton mismatch. In final mode, also require matching DOCX segment IDs and reject unresolved markers.

Test it on a sample with a table, a multi-item cell, and a bold word mid-sentence. Then test a copy with one row removed and a copy with a changed style. Only those two may fail.

## Language file

One short file per target language, `references/<target>.md`, about 15 lines. It trusts the model's knowledge of the language and holds only what the model cannot know:

1. **The brief.** Read the source, work out who writes to whom and in what tone, choose register, vocabulary, and rhythm as a native writer would, and state assumptions in the report.
2. **Decisions of the project.** Variant and spelling, formal and informal address, gendered forms, form of instructions, currency, numbering, layout, terms that depend on context, and terms to flag for review. One line each, taken from the Decisions table.
3. **A closing check.** One address form throughout, fluent text that does not read as translated, local number and date forms, meaning unchanged.

The file holds no phrase list, no typography rules, and no list of false friends, because the model already knows them and a rule list makes the text stiff. Add a rule only when a test shows the translator getting something wrong, and say in the blueprint which test it was. Review the file with the user before the skill ships.

## Build steps

1. Read this document and the upstream files. Resolve the open questions with the user.
Status after the first build:

1. Done. Read this document and the upstream files.
2. Done. `docx_text.py` and `check_structure.py` are tested and listed in the [script index](../scripts/SCRIPTS.md). Visual rendering in Word and LibreOffice and a document authored in Word remain open.
3. Done. The skill, licence files, and German reference exist in `skills/translate-to-german/`. The Text3 trial prompted one clarification to confine slash forms to nouns.
4. Done. Completed the human-text runs listed under Status, ran the blind `Text1-errors` check, and tested a French input.
5. Done. The [README](../README.md) lists the German skill. A later language copies the folder and needs its own name, description, and language file.

## Acceptance checks

- Every row in the disposition table has a result in the skill, and nothing from the dropped rows remains.
- `SKILL.md` is at most 120 lines, the language file at most 30, and the two together under about 10 KB.
- The skill never mentions Agent Teams, `/tmp`, `textutil`, model IDs, or sibling skills.
- Each rule appears once. Severity and type names match everywhere.
- The skill installs and runs without this blueprint and without the submodule.
- The upstream licence and notice ship with each skill, and `data/claude-translation-skill/` is untouched.
- Rules follow the Skill production rules: positive phrasing, short title then full rule, supporting files linked at the step that needs them.
