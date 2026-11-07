# Semantic-layer criteria (four items)

Detection has three layers. Symbol-countable items go to the script (detect.py). Items that need sentence meaning go to the semantic layer (this file, judged item by item by the in-session Claude). Items without enough machine consensus go to human review (metaphor fit; see the human-review zone in SKILL.md).

> **Calibration note:** The thresholds and reference values below come from the Chinese-corpus study (RESEARCH.md). They indicate direction only. Recalibrate on an English corpus with `scripts/compare-human-ai.py` before treating any number as a hard threshold. The labels, however, are closed sets and apply to English prose unchanged.

Usage: first run `python3 scripts/detect.py <file> --candidates --out <candidates.json>`. For each candidate, assign a closed label (only from the labels that criterion lists), a confidence (`high` / `medium` / `low`), and a one-sentence reason. Write the `label`, `confidence`, and `reason` fields back into that candidate so report.py can aggregate them.

**Judging discipline** (lessons from 430k labeling judgments):
- Judge by the criteria only, not by an overall sense of "does this look like AI". Overall impressions are swayed by style.
- Judge each item independently. Candidates deliberately omit the full text, so the model cannot guess from overall style.
- When unsure, use the criterion's fallback label. Do not force a verdict.
- Labels must come from the set listed for that criterion. Do not invent labels.

---

## 1. Synonym renaming (paragraph level): layer 1, rule 10, the strongest actionable signal

**Background**: the same entity or concept is given different substantive names within a paragraph, so readers must make an "X is Y" equivalence link. AI 0.83–0.86 per paragraph vs human 0.49. Heavy paragraphs (≥2 instances): AI 20.6–22.5% vs human 8.4%. **Evidence note: single-model, one-round criterion by Jev. Same direction across models but not iterated, so less robust than the other three items. Re-run first at retest.**

**Candidates**: one per paragraph (`para` field).

**Criterion** (per paragraph, count the substantive-renaming connections; pronouns and ellipsis do not count):

| Label | Criterion |
|---|---|
| `0 groups` | Every entity/concept is referred to with the same (or nearly identical) wording throughout, or appears only once. No renaming occurs. |
| `1 group` | One entity/concept is renamed once within the paragraph, so readers make 1 "X is Y" link. |
| `2 groups` | Two entities/concepts are each renamed, or one is renamed twice. |
| `3+ groups` | Three or more renaming connections. |
| `undecidable` | The paragraph cannot be analyzed. |

**Typical case**: within one paragraph, "optimize / enhance / upgrade / raise" rotate interchangeably for the same change; "footprint → base → project → node → local manufacturing arrangement" are five names for one battery-factory project. Humans repeat the same word.

**Rewrite direction** (after confirmation): revert synonym chains to the original noun. Zero information loss; human exemplars repeat the original noun this way.

---

## 2. Cohesion (inter-paragraph junctions): layer 1, rule 11

**Background**: AI paragraphs are tightly linked (explicit carry-over 98.9% vs human 95.2%). Humans jump naturally (topic shift 7.2% vs AI 2.1%). The real difference is not connective frequency (both low, harmless) but the **background probability of zero jumps**: 93% of AI articles have a chain of ≥6. Chains count junctions, not paragraphs.

**Candidates**: one per inter-paragraph junction (`prev_tail` = last sentence of the previous paragraph, `next_head` = first sentence of the next).

**Criterion** (judge how a = `prev_tail` connects to b = `next_head`. If b opens with a connective, first check whether the logical relation it marks actually holds):

| Label | Criterion |
|---|---|
| `connective but unclear relation` | b opens with a connective (but / therefore / so / meanwhile, etc.), but after reading b, the logical relation the connective marks does not hold, or holds only weakly. **Check this one first.** |
| `explicit carry-over` | Both sides continue the same object or line of argument. The link is natural. Synonyms, pronouns, and ellipsis are allowed; literal repetition is not required. If there is a connective, its logical relation also holds. |
| `related but abrupt shift` | Clearly related (same topic domain), but the transition is abrupt and skips a step. Readers must supply the skipped logic. |
| `unexplained topic jump` | b moves to a new topic essentially unrelated to the previous one, with no transition. |
| `undecidable` | Context is insufficient to judge. |

**Statistical rule**: consecutive `explicit carry-over` junctions = chain length. Report chains ≥6 (AI short texts median 7 vs human 2).

**Rewrite direction** (after confirmation): in a chain, change 1–2 junctions to natural jumps or breaks. Human topics follow the source material and do not pre-lay groundwork for the reader. Prioritize junctions where a connective does not hold.

---

## 3. Colon classification: layer 1, rule 6 (and rule 12)

**Background**: humans use colons more overall (δ−0.37 / −0.31). Only the `conclusion cue` subclass is a true signal, at AI 2.1–2.2× human. `empty cue` runs the other way (humans an order of magnitude higher).

**Candidates**: one per body colon sentence (`colon_before` / `colon_after` / `sentence`).

**Criterion** (judge in priority order, top to bottom; stop at the first match):

| Label | Criterion |
|---|---|
| `quotation or speech` | Before the colon: a person's name or form of address in interview format, or a speech verb (said / stated / wrote / proposed / announced, etc.) immediately after that person as subject. **Takes precedence over all other labels.** |
| `heading/time/ratio metadata or layout` | Before the colon: layout metadata such as heading structure, timestamps, ratio numbers, source or author. (Interview-style "Name: speech" does not count; it belongs to the label above.) |
| `definition or explanation` | Before the colon: a term, concept, or function name. After the colon: its definition or concrete content. |
| `empty cue` | Before the colon: an empty announcement such as "there are several points below," with no claim. After the colon: pure enumeration. **Rejected item: humans use more; do not edit.** |
| `conclusion cue` | Before the colon: one independent, clear conclusive judgment (with a predicate such as is / lies in / depends on / means). After the colon: argument developing that conclusion. **The only true signal.** |
| `other body colon` | Any body colon that fits none of the above. Default bucket. |
| `undecidable` | Context is insufficient. Do not overuse this label just to produce an answer. |

**Typical case**: "These numbers reveal a brutal reality: ……" is a conclusion announcement followed by elaboration.

**Rewrite direction** (after confirmation; applies only to `conclusion cue`): delete the cue and write the content directly, or, if the first half continues the previous text, change only the punctuation.

---

## 4. Highly isomorphic triples: layer 2 (fingerprint; weaker evidence than layer 1)

**Background**: three consecutive sentences share one syntactic skeleton. The broad definition (structurally similar counts) has no discriminating power: AI 71.1% vs human 56.2%. Only the **highly isomorphic** tier differs, at 2.76×: AI 29.4% vs human 10.7%. AI packs the skeleton more extremely (copied word for word); it does not use more parallelism. Only 30% of triples contain serial commas. Seven in ten are pure syntactic reuse of three questions or same-form long sentences.

**Candidates**: consecutive three-sentence groups from coarse signature filtering (`sents` field holds the three sentences). The coarse filter is broad, collecting partial isomorphism too; judging narrows it.

**Criterion** (judge only this triple; the full text is not provided):

| Label | Criterion |
|---|---|
| `highly isomorphic` | Subject, predicate, object, and complements sit in essentially one-to-one positions across the three sentences. The syntactic frame is almost identical; only the specific words differ. |
| `partially isomorphic` | Clear syntactic similarity (e.g., the same subject-predicate frame), but only partial correspondence: not every component matches, or some components are added or missing. |
| `word repetition only` | The sentences repeat some words or phrases, but the overall syntax (who is subject, how the predicate is placed) differs. |
| `semantic parallel only` | The sentences form a content parallel (several items of the same kind), but their syntax differs. |
| `not isomorphic` | No clear repetition or correspondence in either syntax or semantic parallelism. |
| `undecidable` | Context is insufficient, or the sentences are incomplete. |

**Typical cases**: "What is it called? / What function does it carry? / Which ecosystem does it embed in?" (different openings, same skeleton); "Will the service network cover the road I drive home on for the holidays? / Can the car's residual value survive scrutiny? / If this company runs into trouble, who takes responsibility?" (a triad of questions).

**Rewrite direction** (after confirmation): break up one sentence to break the skeleton reuse. Do not delete an item of content. Boundary with the serial-list rule (SKILL.md rule 5): that rule covers multiple items packed into one clause; this one covers a shared skeleton across sentences.

---

## Summary definitions

| Metric | Calculation | Human reference | AI reference | Significance threshold |
|---|---|---|---|---|
| Synonym renaming (per paragraph) | Σ(group count per paragraph) / number of paragraphs | 0.49 | 0.83–0.86 | ≥0.7, or share of heavy paragraphs (≥2 groups) >15% |
| Cohesion chain | Longest run of consecutive `explicit carry-over` junctions | median 2 | median 7 | ≥6 links |
| Conclusion-colon share | `conclusion cue` / total body colons | low | 2.1–2.2× human | High relative share → list as B |
| Highly isomorphic triples | Count of `highly isomorphic` labels | 10.7% (of triples) | 29.4% | Absolute count ≥2 groups → list as B |

All four are statistically significant in the 270-pair matched corpus (Chinese). Synonym renaming uses a single-model Jev criterion and is less robust than the other three. Rewriting still follows the allowlist and confirmation process in SKILL.md.
