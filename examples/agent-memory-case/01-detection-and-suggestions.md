# Stage 1 | Detection and Suggestions (before revision)

Article: "Agent Memory: Why Your AI Assistant Keeps Forgetting" (English worked example, translated from a Chinese article; the Chinese source is not included).

## Scope and criteria

The original is 1,829 words with 46 body paragraphs, per `detect.py`. The script counted fixed constructions, punctuation and structure, then extracted 79 semantic candidates: 29 paragraphs for synonym renaming, 34 junctions for cohesion, 16 colon sentences and 0 isomorphic triples. Each candidate was judged against `references/semantic-criteria.md` with a closed label, a confidence and a one-sentence reason (`data-semantic-labels.json`).

Significance follows the skill's existing method. "Significant" below refers to **human-vs-AI differences in the research corpus**. This report does not recompute significance for this article, and does not use it to judge whether the author is an AI. Whether a single article is worth editing also depends on where the hits fall and what they do.

## Metrics

| Metric and layer | Result in this article | Research reference | Judgment |
|---|---|---|---|
| "Not A but B" contrast: script | 3 hits, 1.640 per 1k words (line 72 is a false positive) | Human ≈0.22, AI ≈0.73 per 1k chars | Lines 13 and 76 are real and are edited. Line 72 is a false positive and is kept. |
| Dense lists ≥3: script, model filters | 9 hits, 4.921 per 1k words | Human ≈1.78 per 1k chars | Edit 2 body lists (lines 25, 47). Keep 7 (reasons below). |
| Conclusion-cue colon: semantic | 16 colons: 6 conclusion cue, 3 headings, 2 quotation or speech, 2 definition, 2 other body, 1 empty cue | Only the conclusion-cue class differs (AI ≈2.1–2.2× human). The total colon count is not the signal. | Edit the 6 conclusion cues. The script's cue-phrase rule now finds 5 (lines 7, 31, 49, 63, 86); line 7 is kept (see below). |
| Synonym renaming: semantic, paragraph level | 5 groups across 46 paragraphs (≈0.11 per paragraph); 0 paragraphs with ≥2 groups | Human ≈0.49, AI ≈0.83–0.86 per paragraph | Below threshold. Not in edit scope. |
| Cohesion chain: semantic, junction level | 34 junctions: 26 explicit carry-over, 8 related but abrupt shift. Two carry-over chains of 6 (lines 33–47) and 9 (lines 59–86) | Threshold ≥6; human median 2, AI median 7 | Flagged. Pending human review (see below). |
| Isomorphic triples: script | 0 candidates | Human ≈10.7%, AI ≈29.4% of triples | Manual reading finds one group at line 45. Low priority. |
| Em dash: fingerprint | 7 hits, 3.827 per 1k words | Opus heavy, GPT light | All 7 separate a term from its definition or a list item. Keep with reason. |
| Semicolon: fingerprint | 4 hits, 2.187 per 1k words | GPT fingerprint (δ +0.80) | Split 3 (lines 59, 82, and 76 through the contrast edit). Keep the one in a list item (line 67). |
| Quotation marks: fingerprint | 31, 16.949 per 1k words | Opus uses fewer (δ −0.67) | Report only. |
| Sentence-length CV: structure | 0.662 | Human ≈0.54, AI ≈0.46 | Report only. Do not chase a target value. |
| Headings | 0 detected | — | Known detector gap: English headings ("01 The Misnamed Problem") are not recognized. |

## Hit examples and planned edits

Line numbers refer to `00-original.md`.

**1. Contrast reversal.** Line 13: "But what decides whether you can find that bag of shrimp … is not the refrigerator's capacity. It is which shelf you put it on …" Line 76: "It is not about storing more; it is about separating things clearly." Both put the negated half first and carry a paragraph's point. Planned edit: state the point directly and keep the negated information. Line 13 becomes "the refrigerator's capacity does not decide whether you can find that bag of shrimp … What matters more is which shelf …". Line 76 becomes "Beyond how much to store, it is also about separating things clearly." Do not delete "capacity" or "storing more", so the argument stays the same.

**2. Dense lists.** Line 25, "what to search for, how many times to search, and whether to use what it finds": the three conditions are all needed, so fold them into one action. Planned: "what to search for and how often it searches, then whether to use what it finds." Line 47, "For free users, lightweight conversations, and scenarios that need fast responses": planned: "For free users and lightweight conversations, and wherever a fast response is needed." Line 15, "the right content, in the right form and the right order", was not flagged by the script but is a three-part list. Planned: "in the right form and order."

Kept, with reasons: line 13's list (the three cues are the analogy's concrete points); line 39 (three distinct examples, each with a different syntax); lines 67, 68, 70 (inside Markdown list items, which are not edited); line 86 ("cheap writes, rigorous updates, and zero LLM cost", three separate requirements of one trade-off).

**3. Conclusion-cue colons.** Lines 31, 49, 51, 63, 86 and 92. Each sentence has an independent judgment before the colon ("The technical reason is actually simple", "Core memory solves a different problem", and so on). Planned: if the first half adds information, keep it and end the sentence with a period; if the sentence needs a bridge, use a comma or "namely". Example, line 31: "The technical reason is actually simple. Every time a new conversation …". Example, line 92: "But it determines something fundamental, namely whether trust can truly accumulate …".

Kept colons: the line 7 colon ("faces the same awkward fact:"), which the script flags but the semantic pass labeled other body colon, because the text after it is the specific content of the fact rather than an independent conclusion (low confidence); the title and section headings (layout); the quote lead-ins at lines 5 and 59 (quotation or speech); the definition colons at line 45; the empty cue at line 9 ("a buzzword for this:"), which is a rejected class; the signpost at line 72 and the lead-ins at lines 35 and 65.

**4. Parallel skeleton.** Line 45 has three consecutive sentences with the same frame ("X is …: you …"). Planned: reorder one clause only: "You carry core memory everywhere, like an ID card." The three images (sticky note, ID card, filing cabinet) stay.

**5. Semicolons.** Lines 59 and 82 each join two independent clauses. Planned: split into two sentences.

## Not in revision scope

- **Line 72**, "isn't settled yet," but": false positive. It is an ordinary contrast with "but", not the "not A but B" construction.
- **Synonym renaming**: 5 groups, none in a paragraph with ≥2 groups. No concentrated renaming problem.
- **Cohesion chains** (lines 33–47 and 59–86): flagged, but not edited. The rule allows one natural break per chain, but no junction here has a broken connective. The only break would need a bridge sentence the author did not write, which changes content and structure. Tagged `pending / human review`.
- **Metaphors** (refrigerator, sticky note, ID card, filing cabinet): kept. Fit is a human-review item.
- **Em dashes** (lines 37, 39, 41, 67–70): definition and list separators. Kept.
- **Quotation marks, sentence-length CV, lexical variety, isomorphic pairs**: report only.

## Recommendation and pending confirmation

Recommended scope: 2 contrast reversals (lines 13, 76); 3 dense-list edits (lines 15, 25, 47); 6 conclusion-cue colons (lines 31, 49, 51, 63, 86, 92); 2 semicolons (lines 59, 82); 1 parallel clause (line 45). Keep facts, numbers, qualifiers, quotations, metaphors, lists, sections and paragraph order. Retest with the same script.

`02-revised.md` applies this scope. Please confirm, or name a pattern type to keep, before the revision is used.

Detection data: [script results, before](data-detect-before.json) · [per-item semantic labels](data-semantic-labels.json).
