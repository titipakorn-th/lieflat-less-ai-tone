# Lieflat Less AI Tone | Full Case

Article: 《Agent 的记忆问题：为什么你的 AI 助手总在失忆》 (“Agent Memory: Why Your AI Assistant Keeps Forgetting”)

This folder keeps detection, suggestions, revision, side-by-side comparison and retest for one article together, for reading or as a worked example of the skill workflow.

| Stage | Output | Purpose |
|---|---|---|
| Source | [Original](00-original.md) | Check facts and the starting text. |
| Stage 1: detection | [Detection results and suggestions](01-detection-and-suggestions.md) | Script and semantic metrics, research baselines, example sentences from the original, concrete edits and what is kept. Wait for the user's reply at this stage. |
| Stage 2: revision | [Revised full text](02-revised.md) | Deliver the ready-to-use article after the user replies. |
| Stage 2: comparison | [Side-by-side HTML](03-side-by-side.html) | Review deleted and added text paragraph by paragraph. Toggle "Changes only" / "Show full text". |
| Stage 3: retest | [Retest findings](04-retest.md) | Check remaining hits, false positives and content preservation. |

Data: [Script detection (before)](data-detect-before.json) · [Per-item semantic labels](data-semantic-labels.json) · [Script retest (after)](data-detect-after.json)

**Chronology note**: this revision was generated earlier in the conversation. The skill workflow was later changed to "show detection and suggestions, wait for the user's reply, then revise". This case arranges the existing original and revision as stage outputs so the new flow can be reviewed. It does not mean the new flow can skip the user's reply.
