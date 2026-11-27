# Project scripts

Run these commands from the repository root. The skill ships with both scripts.

| Script | Purpose | Example |
| --- | --- | --- |
| `docx_text.py extract` | Extract labeled DOCX segments as JSON. | `python skills/translate-to-german/scripts/docx_text.py extract SOURCE.docx -o segments.json` |
| `docx_text.py inject` | Build a translated DOCX and set its proofing language. | `python skills/translate-to-german/scripts/docx_text.py inject SOURCE.docx translation.json FINAL.docx --lang de-DE` |
| `check_structure.py` | Check structure and flag digit differences. Final mode also checks for unresolved markers and missing DOCX segment IDs. | `python skills/translate-to-german/scripts/check_structure.py SOURCE.docx FINAL.docx --final` |
