# Lieflat Less AI Tone | Full Case

Article: "Agent Memory: Why Your AI Assistant Keeps Forgetting" (English worked example, translated from a Chinese article).

This folder keeps detection, suggestions, revision, before/after comparison and retest for one article together, as a worked example of the skill workflow.

| Stage | Output | Purpose |
|---|---|---|
| Source | [Original](00-original.md) | Starting text and facts to check. |
| Stage 1: detection | [Detection results and suggestions](01-detection-and-suggestions.md) | Script and semantic metrics, research references, example sentences with line numbers, planned edits and what is kept. |
| Stage 2: revision | [Revised full text](02-revised.md) | The ready-to-use article after the planned edits. |
| Stage 2: comparison | [Before/after HTML](03-before-after.html) | Deleted and added text, with a metric table and the semantic judgments. |
| Stage 3: retest | [Retest findings](04-retest.md) | Remaining hits, false positives, what was kept and why, and the information-conservation check. |

Data: [Script detection, before](data-detect-before.json) · [Script detection, after](data-detect-after.json) · [Per-item semantic labels](data-semantic-labels.json)
