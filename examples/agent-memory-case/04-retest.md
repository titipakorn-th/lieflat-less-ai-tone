# Stage 3 | Retest Findings (after revision)

Compared: `00-original.md` against `02-revised.md`, both run through the same `detect.py`. Fourteen lines changed, in 14 paragraphs out of 96 lines. The title, paragraph order, headings, quotations, the numbers and the three memory layers are unchanged. The counts are an auxiliary check, not a quality score.

| Check | Before | After | Conclusion |
|---|---:|---:|---|
| Contrast reversal ("not A but B") | 3 | 1 | Lines 13 and 76 rewritten. The remaining hit (line 72, "isn't settled yet, but") is a false positive, kept. |
| Dense lists ≥3 | 9 | 8 | Line 47 cleared. Line 25 rewritten but still listed: all three conditions are its substance. Lines 13, 39, 67, 68, 70 (×2) and 86 kept by rule (see below). |
| Conclusion-cue colon: script screen | 5 | 1 | Lines 31, 49, 63 and 86 rewritten. The remaining hit, line 7 ("the same awkward fact:"), is kept; see below. |
| Conclusion-cue colon: semantic (6 judged) | 6 | 0 | Lines 31, 49, 51, 63, 86 and 92 rewritten. The colons left in the text are headings, quotation lead-ins, definitions, the empty cue at line 9, the signpost at line 72 and the line 7 colon. |
| Empty lead-in to list (rejected) | 2 | 2 | Rejected feature. Not edited. |
| Em dash (fingerprint) | 7 (3.827/1k) | 7 (3.821/1k) | Kept: all seven separate a term from its definition or a list item. |
| Semicolon (fingerprint) | 4 (2.187/1k) | 1 (0.546/1k) | Lines 59 and 82 split. Line 76 rewritten. The remaining one is inside a Markdown list item (line 67), kept. |
| Quotation marks (fingerprint) | 31 (16.949/1k) | 31 (16.921/1k) | Report only. |
| Sentence-length CV | 0.662 | 0.671 | No change by design. Not chased. |
| Isomorphic pairs per 100 paragraphs | 4.35 | 4.35 | Line 45 changed in one clause. The coarse pair count is unchanged. |
| Isomorphic triples per 100 paragraphs | 0 | 0 | The script found no triple candidate before or after. |
| Lexical variety (MTLD) | 133 | 135 | Small change. Report only. |
| Synonym renaming (paragraph level) | 5 groups in 46 paragraphs | Not re-judged | Below the ≥2-groups-per-paragraph threshold before revision. No edits. |
| Cohesion chain ≥6 | 2 chains (6 and 9) | Unchanged | Pending human review. Not edited (see below). |

Word count by `detect.py`: 1,829 before, 1,832 after.

## What was kept, and why

- **Line 13 list** ("which shelf …, whether you labeled it, and where your eyes go first"): the three cues are the concrete points of the refrigerator analogy. Cutting one loses a mapping.
- **Line 39 list** (three examples): distinct items with different syntax. Splitting them would add length without adding information.
- **Lines 67, 68, 70 and the semicolon at 67**: inside Markdown list items. The skill does not edit list structure.
- **Line 86 triple** ("cheap writes, rigorous updates, and zero LLM cost"): three separate requirements of one trade-off. Merging them would drop one.
- **Line 25 list**: the three conditions (what to search, how often, whether to use the result) are the sentence's substance. Folding them further would drop "how often".
- **Em dashes** at lines 37, 39, 41 and 67–70: term-definition separators. Replacing them with colons would move them into the colon pattern.
- **Line 7 colon** ("faces the same awkward fact:"): the script flags it as a cue-phrase colon, but the semantic pass labeled it other body colon. The text after it is the specific content of the fact, not an independent conclusion. Low confidence: converting it to a period would also cost no information, so a reviewer may prefer that.
- **Line 72** ("isn't settled yet," but): script false positive. It is an ordinary contrast, not "not A but B".
- **Cohesion chains** (lines 33–47 and 59–86): no junction has a broken connective. Breaking one would need a bridge sentence the author did not write. Tagged pending human review.

## Information-conservation check

- **Numbers and dates unchanged**: 10 hours, $30, 9 minutes, 0.9169, about 0.68, last 7 days, 79%, more than 10,000 tokens, ¥400,000–500,000, two weeks, three hours, three rounds, six schools.
- **Names unchanged**: LangChain, OpenWiki Brains, OriginTrail, MemMachine, Mem0, Letta, BM25, LoCoMo, generic-roster.
- **Quotations unchanged**: "In the end, nothing accumulates.", "Hello, may I ask who is calling?", "I'll remember.", "Why are we building this feature this way?", "hallucination" and the rest.
- **Qualifiers**: all kept except the reworded contrast at line 76. Line 25 changed "how many times to search" to "how often it searches"; the same information.
- **Line 76, for author review**: "It is not about storing more; it is about separating things clearly" became "Beyond how much to store, it is also about separating things clearly." The new sentence no longer denies that storage volume matters; it adds separation on top. This is the one wording change that moves the stance slightly, so check it first.
- **Line 13**: "is not the refrigerator's capacity" became "does not decide whether …". The claim is the same, and "capacity" is kept.
- **Line 47**: "scenarios that need fast responses" became "wherever a fast response is needed". Equivalent.
- **Line 49**: the colon became "the question". The claim is the same.

## Open items

- Cohesion chains of 6 and 9 remain flagged. They are a human-review decision: either accept the explicit carry-over, which is how the argument reads, or add a bridge sentence.
- Semantic labels were produced for the original only. The six conclusion cues were re-checked by reading, not by re-running the classifier on the revision.

To read the edits, open the [before/after page](03-before-after.html). To copy the final text, use the [revised full text](02-revised.md).
