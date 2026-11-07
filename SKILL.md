---
name: lieflat-less-ai-tone
description: Three-layer "less AI tone" pass for English prose. The script produces a graded report (A mechanical fix / B suggested fix / C report only / X rejected / F fingerprint / H human review). The semantic layer adds judgments (synonym renaming, cohesion chains, conclusion-cue colons, isomorphic triples). First deliver a readable pre-edit report with this article's metrics, research significance, original example sentences, and concrete fixes. After the user replies, rewrite using the allowlist rules, retest, and produce a before/after report (Markdown by default, same format as the manuscript). Rules come from a two-round study of Chinese corpora and are not calibrated for English; treat thresholds as direction only. Use for cleanup of finished writing.
---

# Less AI Tone v2 (English)

Identify and rewrite AI writing traces in English prose. The workflow is **detect first, explain findings and fixes with metrics and examples, wait for the user's reply, then rewrite and deliver with a retest**.

> **Calibration note:** Reference values and thresholds come from the two-round study of Chinese corpora (see RESEARCH.md). They indicate direction only, not calibrated English thresholds. Recalibrate on an English corpus with `scripts/compare-human-ai.py` before treating any number as a hard threshold. All densities are per 1k words.

The report must be professional and easy to read: say which features are significant in the research corpus, how many this article actually hits, and why those spots are worth changing. The model does the item-by-item screening. It does not hand dozens of candidates and a metaphor list to the user for item-by-item decisions. The user replies "apply the suggestions" to proceed, or adjusts the scope in one sentence.

The rules come from two measurement rounds: round one, a 629-article control corpus; round two, 270 matched pairs (same topic, same facts) retested, plus 430k semantic judgments. The matched retest overturned three v1 rules (see the X-grade list below). Those rules appear only in the detection report and are never executed.

Detection has three layers. **Symbol-countable items go to the script** (detect.py regex and structural metrics). **Items that need sentence meaning go to the semantic layer** (the in-session model judges item by item per [references/semantic-criteria.md](./references/semantic-criteria.md)'s closed criteria). **Items where machines don't agree enough go to human review** (metaphor fit, implicit metaphor, personifying metaphor). The report lists them in the human-review zone only; the model does not judge them.

## Workflow (follow the order)

### Step 1: Script detection

```bash
python3 scripts/detect.py <file or directory> [--max-hits 5] [--json]
```

Get the graded report. Grade meanings and grading basis are in [DETECT.md](./DETECT.md). **Always archive with `--json` before editing**; the step 4 comparison report needs it.

### Step 1.5: Semantic-layer judgment (mandatory for single files; optional for batch directories)

```bash
python3 scripts/detect.py <file> --candidates --out /tmp/candidates.json
```

For the four candidate types (synonym-renaming paragraphs, inter-paragraph junctions, colon sentences, isomorphic triples), give each one a `label`, `confidence`, and `reason` per the criteria in [references/semantic-criteria.md](./references/semantic-criteria.md), and write them back to the JSON. Judging discipline (lessons from 430k labeling judgments): judge by the criteria, not overall feel; judge each item independently, without the full text; when unsure, use the fallback label; never invent labels.

A typical article yields dozens of candidates (40–80 in the study's 3k-character sample). Judge them in-session. Afterwards, compute the four numbers using the summary definitions at the end of the criteria file: renamings per paragraph, longest cohesion chain, conclusion-colon share, and isomorphic-triple count.

### Step 2: Show the detection results and suggestions; wait for the reply

After reading the script report and the four semantic-layer summaries, deliver a **professional, readable pre-edit detection report** to the user, then end the turn. Length depends on the article and the number of issues. Do not give a one-line impression, and do not paste raw script output. The report must include at least:

1. **Method and definitions**: state what the script counted and what the semantic layer judged. Give this article's word count, paragraph count, and candidate count. Clearly distinguish "statistically significant in the research corpus" from "a single hit in this article." Without a single-article significance test, do not claim this article is statistically significant, and do not conclude from it that the author is AI.
2. **Metric results and where hits go**: use one compact table listing this article's layer-1 cross-model metrics and layer-2 single-model fingerprint hits. For items that can be pinned to a sentence, state the **raw hit count, valid hit count, to-edit count, and keep count**, plus this article's density, the research reference, and the evidence strength. Whole-document distribution metrics such as sentence-length CV and structural variance report only the measured value and its disposition; do not manufacture per-sentence hit counts. Zero raw hits may be listed briefly. Even if an item falls below the action threshold or is kept, it must not be removed from the report. Counting bases differ across rounds; do not mix multipliers.
3. **Examples and fixes**: for each metric proposed for action, quote 1–2 original sentences with their locations, explain how the hit works and its concrete effect on reading, then give an actionable fix. Short sentence sketches are fine, but they are not a formal revision: at this stage, do not write or deliver the full revised text. Preserve facts, qualifiers, and information points. Do not give vague advice such as "make it more natural."
4. **Exclusions and scope**: for each kept or excluded metric, state the count and reason category, with at least one locatable example. Normal uses such as headings, lists, and quotations, low-priority hits, and specific reasons for keeping fingerprint items go here. Finally, summarize the proposed edit scope and the kept boundaries. Ask the user only to reply "apply the suggestions" to the **whole set of suggestions**, or to request adjustments. Do not ask for item-by-item decisions.

**Never silently drop items from the hit list.** Save raw script hits and semantic candidates in full in the JSON first. Model review may only tag each item as `to edit` / `keep` / `false positive` / `pending or human review`, with a reason. It may not change the raw counts or remove disliked candidates from the list. A semantic "does not meet criteria" result is a recorded judgment and counts toward the gap from raw candidates to valid hits. If the user provided a file, keep a traceable item-by-item results file. The main report explains dispositions with counts and typical examples; the user does not need to decide item by item.

**Layer 1 and 2 default: valid, locatable hits are listed as `to edit`.** Research metrics are for screening which patterns are worth handling. A low count, low density, or a count below the whole-article signal line only affects priority in the report. It cannot alone justify letting a valid hit pass. Treat `keep` as an exception that needs evidence: state specifically why the rhetoric, quotation, terminology, semantic relation, or author style at that spot cannot be replaced, or explain that even a minimal rewrite would lose information. Do not keep an item with only "it reads naturally," "there's only one instance," or "the model may not do this" as the reason. If the criteria cannot settle an item, tag it `pending / human review`, list the original sentence, and do not assume it has no problem. Before the user replies, only propose; do not edit the text.

The format is mainly a metrics table with explanatory paragraphs. Terms are fine but must be explained. Numbers need definitions and references. Examples must be locatable in the original. The goal is for the user to see clearly "detection basis → hits in this article → original example → concrete fix," not just adjectives or a string of A/B/C grades. The main report does not include all candidates, item-by-item checkboxes, or the full list of metaphors.

Full example: [examples/agent-memory-case/README.md](./examples/agent-memory-case/README.md). It includes the pre-edit detection and suggestions, the full revised text, a side-by-side HTML comparison, and the retest conclusions. (The case is a Chinese article; use it for workflow shape, not for English thresholds.)

Example phrasing (one metric paragraph only; illustrative numbers):

> The script found 2 instances of "not A but B" contrast in this article, density 0.763 per 1k words. The round-one human reference is about 0.22 per 1k words (Chinese corpus, direction only), and in the matched retest, GPT and Opus were also high in the same direction. Line 13, "The bottleneck isn't the server's capacity but the queue design," and line 76, "It isn't about storing more but about sorting clearly," both sit in paragraph conclusions. Suggest stating the judgment directly while keeping the qualifiers (capacity, storage volume). Do not delete the contrasting information wholesale.

This report is the **only pre-edit checkpoint**. After it is sent, stop at the detection stage. **Do not rewrite the article until the user replies.**

Before proposing, the model reviews each hit itself, and the review must leave a trace. For A-grade false positives such as headings and quotations, tag them `false positive`; do not subtract them from the raw count. For A/B locatable local hits that can be safely rewritten, tag `to edit` by default; keeping one requires a specific reason for each. The semantic layer is verified against the closed criteria (key report thresholds: a paragraph with ≥2 renaming groups, chains of ≥6 links, conclusion colons, and ≥2 groups of highly isomorphic triples), and negative judgments are also recorded. Items below the whole-article threshold that have the same kind of problem in this sentence may be listed as low-priority `to edit`; they must not be written as statistically significant for this article. Do not exclude them just because the count is low. If an item cannot be determined, tag it `pending / human review` and show it; do not zero it out. **Whole-document distribution metrics such as C-grade sentence-length variance and section geometry must not be presented as errors in any particular sentence. Report the measured value; suggest a fix only if it is locatable and does not break the article's structure. H-grade metaphors, implicit metaphors, and personification go to human review. Do not let the model pretend it can judge fit.** When the user explicitly asks to handle C or H items, follow the corresponding constraints. Quotations must never be altered, even when they are in scope.

When the user replies "OK," "apply the suggestions," "go ahead," or similar, proceed directly to step 3 per the report's suggestions. Do not re-confirm. When the user gives revision notes, adjust to them and proceed to step 3. If the reply is only a question or explicitly asks to hold off, answer or pause first. Do not treat silence as agreement. When the user says "apply all," it means the locally located A + B + semantic + F hits that were reviewed and tagged `to edit`. It excludes X, non-locatable C items, and H items pending human review. If the user gives explicit instructions for C or H items, follow them.

### Step 3: Rewrite

After the user replies to step 2, change only the items included in the plan the user accepted or adjusted. Rewriting principles are below. Log every edit as "original → revised + rule number" for review in step 4.

### Step 4: Retest + before/after report

Re-run `detect.py` on the revised draft (archive with `--json`), then generate the before/after report:

```bash
python3 scripts/detect.py revised.md --json > /tmp/after.json
python3 scripts/report.py original.md revised.md /tmp/before.json /tmp/after.json \
    --semantic /tmp/candidates_labeled.json --out less-ai-tone-report.md
```

**Default output is Markdown**: same format as the user's manuscript. The comparison section is the full revised text, with edits marked as `<del>original</del><ins>new text</ins>`. Other Markdown markup is left as is, so the whole block can be copied back into the writing workflow directly. For a web version, add `--format html` (red strikethrough for deletions, green insertions; view with `open` in a browser).

The report has three parts: at the top, a before/after metrics table (with a human-reference column); in the middle, the graded issue list plus semantic-layer judgments; at the bottom, the before/after comparison.

Reading the retest: for locatable A/B/semantic/F hits that were reviewed and tagged `to edit`, check whether the edit was made. False positives such as headings and lists may stay; explain them in the report. For F fingerprint density changes, give a directional reading and do not force it to zero. For C-grade structure metrics (sentence-length CV, isomorphic pairs per 100 paragraphs), report the numbers but **do not chase a target value**. Pushing sentence-length CV from 0.37 to 0.67 is mechanical variation, which is worse than not editing.

## Rewrite principles (for when AI rewrites come out badly)

Common failure modes when a model rewrites AI tone, and countermeasures:

**1. Minimal change.** For each hit, change only what is necessary to fix that problem. No drive-by polishing, no swapping words that are fine, no adjusting tone or level of detail. When in doubt, keep the original. The more you change, the more you get wrong. Every extra edit is a new semantic risk.

**2. Preserve information.** Keep the original's views, facts, and qualifiers intact. For names, numbers, dates, quotations, sources, and causality, every content word must be traceable to the original after rewriting. Changing "may" to "will" alters the strength of a judgment. That is tampering, not removing AI tone.

**3. Do not manufacture variation.** Measured dispersion of sentence and paragraph length shows no human–AI difference (shown in v1, confirmed by matched retest). Do not make sentences alternate long and short, or chop paragraphs up, to "look human-written." Rhythm issues are noted only in the C-grade report and are not edited sentence by sentence by default.

**4. Leave structure alone.** Keep heading levels, section order, paragraph order, lists, tables, quotations, and code block positions exactly as they are. **Do not change subheading numbering** (overturned by matched retest; see the X-grade list).

**5. Read the style reference first.** If the same directory has a style document (a writing style guide, or a style guide such as `voice-DNA.md`), read it first. On conflict, the style document wins: it reflects the target author's real writing, not AI traces. If the author habitually uses em dashes, do not delete them under the fingerprint rule.

**6. Three self-checks after editing.**
- Can every edit be matched to a plan item and rule number? If not, revert it.
- Does every content word have a source? If not, revert it.
- After retest: are the A/B items that needed handling cleared, are kept false positives explained, and have C-grade metrics avoided large swings?

## When not to edit

- Article framework (see principle 4)
- Dialogue and colloquial style: already natural expression
- Questions, rhetorical questions, and question-form subheadings: humans use far more questions in body text than AI does, so deleting them makes the text look less human
- Literary expression: judge parallelism and metaphor in essays and fiction by the original style
- Genre requirements: academic, news, and official documents need not have "I" / "you" forced in
- Code blocks, foreign-language passages, and quotations
- **Ordinal subheadings, "this means" restatements, empty lead-in lists, and vague summaries (not edited even if the same paragraph has data).** These were rules in v1/v2, but the 270-pair matched retest reversed their direction or showed net zero (humans use them more, or the two sides are symmetric). Never edit. The detection report's X section flags them to prevent wrong edits.

---

## Rewrite rules (in priority order)

Measured figures in the rules: those marked "matched retest" come from the 270-pair same-topic, same-fact corpus (GPT-5.6 135 articles + Opus 4.6 135 articles vs 270 human articles). The rest come from the round-one 629-article control. All were measured on Chinese prose; the English port keeps only items whose pattern has an English form, and recalibration is pending. Only items that passed both rounds are kept as rules.

### 1. Contrast reversal

Set up a misunderstanding the reader does not hold, then knock it down. Patterns: "not X but Y," "not so much X as Y," "on the surface … in fact …," "seems … but actually …," "you might think … but actually …," "A doesn't matter; B does." The list is examples only: any wording of the same move must be changed.

Measured: round one, AI 0.73 / human 0.22 (3.4×). Matched retest: GPT δ+0.88 / Opus δ+0.72. Both rounds point the same way. This is the strongest pure-writing signal.

Fix: state the judgment directly, first, and give the basis after it.

> ❌ The real barrier isn't technology, it's cognition.
> ✅ The real barrier is cognition.

> ❌ You might think users care about how many features there are, but what they really care about is whether they can use it right away.
> ✅ Users first care about whether they can use it right away.

### 2. Cue-phrase colon

The part before the colon is a cue phrase such as "In short," "The core is," "The key lies in," or "The reasons are as follows." It announces on the author's behalf that a conclusion follows.

Measured: round one, AI 0.29 / human 0.08 (3.8×). Matched retest, semantic-layer conclusion-cue colons: AI at 2.1× human. Same direction in both rounds.

Two fixes. If the cue phrase carries no information, delete it and write the content directly. If the first half continues the previous text, keep it and replace only the colon with a period or comma. Test: would deleting this half lose information or break the connection?

> ❌ In short: the plan costs too much.
> ✅ The plan costs too much.

> ❌ The reasons are as follows: delivery was late, and the budget also overran.
> ✅ Delivery was late, and the budget also overran.

**Empty lead-in to a list ("Here are the typical scenarios I've seen:" + list) is not edited.** Round one measured 9.4×, but the matched retest reversed direction: humans are an order of magnitude higher. In catalogue-style long-form writing this is normal. Listed as X-grade.

Also not edited: colons introducing a person's direct speech; colons in subheadings; colons within list items; general-then-specific constructions such as "What people are good at: judging business logic" (usage varies 6.6× among humans, so no stable difference is measurable); URLs and code.

### 3. Opening formula

"To put it bluntly," "To be frank," "Conclusion first," "Long story short." Delete them and state the judgment directly. Round one: 3.2×. Small volume, but stable.

### 4. Stock framing (two types)

Only two structures are handled: topic-shell frames and sentence-initial connectives. Anything beyond these markers is kept even if it reads stiffly. Round one screened 5 of 18 translationese candidates; the matched retest then overturned one more ("this means"), leaving these two types. The Chinese-only long pre-modifier and "when…" clause rules were dropped in the English port (no English counterpart).

**Topic-shell frame** (detector: `Topic-shell frame`): "When it comes to…," "In terms of…," "As for…," "With regard to…," "As far as X is concerned." When the sentence already has this object as its subject, delete the shell.

> ❌ For early teams, hiring is the hardest thing.
> ✅ The hardest thing for early teams is hiring.

> ❌ When it comes to hiring, early teams struggle most.
> ✅ Early teams struggle most with hiring.

**Sentence-initial connective** (detector: `Sentence-initial connective`): "However," "Therefore," "Moreover," "Furthermore," "Additionally," "Importantly," "Notably," especially when consecutive paragraphs open this way. Move it after the subject, swap it for "but" or "in fact," or drop it. Keep it when the argument truly needs an explicit signpost.

> ❌ However, the test failed.
> ✅ The test failed, but the cause is still unclear.

**"This means" and "this shows" restatements are not edited.** Round one listed it at 0.15 per 1k chars. The matched retest reversed direction on all three counting definitions (human 0.027 vs AI 0.016 per 1k chars). Listed as X-grade.

### 5. Dense serial lists (detector: `Serial list ≥3`)

A series of three or more items in one clause, such as "speed, accuracy, and cost control." Round one: AI 3.21 / human 1.78 (per 1k, Chinese corpus). Matched retest: dense parallel lists AI 1.45×. Same direction in both rounds.

Fix: summarize if you can. If every item must stay, change the syntax of one item so they don't share one structure. Do not edit statutory provisions, configuration lists, or anything that must be listed in full, or the inside of Markdown lists. Short in-clause parallelism ("raise efficiency, cut costs, improve the experience") is used by humans no less than by AI, so it is outside this rule.

### 6. Adjacent sentences with the same structure

Adjacent sentences share one syntactic skeleton: same comma positions, same order of components, same ending. Round one per 100 paragraphs: AI 9.41 / human 4.81. Matched retest: highly isomorphic pairs AI 1.6× (triples 2.75×). Same direction in both rounds.

Fix: break up one of the sentences by merging, splitting, reordering, or shortening it. Edit within the sentence only; do not change paragraph order or delete information.

> ❌ Cloudflare published a long post proposing a credential-isolation framework. AWS open-sourced Kiro Crew, a multi-agent orchestration platform. Y Combinator also released its internal tool, QM.
> ✅ Cloudflare published a long post proposing a credential-isolation framework. AWS and Y Combinator each open-sourced an orchestration tool: Kiro Crew, a multi-agent platform, and QM, which ships with a human-approval gate.

When parallel examples are padding, merge like items and compress minor ones into half-clauses. Information is not deleted; only the emphasis changes. Narrative progression (what happened first, what came of it) does not count. Do not edit list-style paragraphs, dialogue quotations, or literary parallelism.

### 7. Personifying metaphors (human-review zone; not auto-edited)

Comparing a tool or system to an idealized person: "like a wise mentor," "a tireless junior reviewer." Round one: 7.3×. Matched retest: personifying metaphors AI 1.2× (weak signal). But both sides are near saturation (99.3% / 97.4% of articles contain personification). The difference lies not in "whether" but in fit, and models cannot judge fit (same family as metaphor fit; inter-model agreement 0–40%).

Moved to the human-review zone on 2026-10-26: models are unreliable on fit. By default, keep metaphors and personification, and do not interrupt the rewrite with a whole-article list. When the user explicitly asks to check H-grade items, list the matching original sentences for human review, **without grading or opinion**. When the user explicitly asks to turn one into a non-metaphor, state plainly what the tool or system actually does.

### Handling F-grade fingerprints

**A fingerprint is a model-usage tendency in the research corpus. It cannot be used to infer which model wrote this article.** Do not ask the user for the generating model. Texts of unknown origin are still checked, but the report says only "this article's density or usage is similar to fingerprint direction X," not "this article came from model X." For locatable, safely rewritable fingerprint usage, propose the minimal fix by default. Count and density are for ranking, not a per-item exemption. Semantic judgment only verifies specific usage; do not present a single-model difference as a cross-model general fact.

- **Em dashes**: more than 2 per 1k words is the priority threshold, not the only entry point. Check each one. When it is a decorative pause, or it suspends a conclusion that could be stated directly, propose an edit by default. Keep it when it carries necessary emphasis, inserts an explanation, or conveys a voice or tone and an edit would lose that effect, and state the reason.
- **Semicolons**: check each one for whether it can safely become a period. When consecutive semicolons make one sentence carry too many layers, prioritize splitting. Keep it when there is a real parallel hierarchy or logical correspondence and splitting would lose the relation.
- **Quotation marks**: Opus using few is not a reason to add quotation marks. Handle them according to quotations, proper names, and the original's markup. Do not add or remove them based on the fingerprint.
- **Highly isomorphic triples**: confirm with the closed semantic criteria in rule 13. Prioritize when the whole-article report threshold is met. A single group with genuinely mechanical reuse may be listed as low-priority `to edit`. Keep deliberate rhetoric, lists, and three-event sequences in narrative, and state the basis.

For locatable F-grade candidates that can be edited, propose the fix by default. To keep one, name the specific function this expression cannot lose. Do not let it pass just because the count is low or the author model is unknown. Missing-type fingerprint features such as "too few quotation marks" and whole-document features such as sentence-length distribution have no per-instance hits to edit. Report only their direction, or handle them only when there is an independent problem. Single-model significance in the research does not mean a single hit in this article is significant.

### 8. Em dashes (fingerprint rule; density sets priority)

**At more than 2 per 1k words, handle first. Below that line, still check each instance for safe rewriting.** Matched retest shows extreme model divergence: GPT −0.54 (even fewer than humans) / Opus +0.95 (more). Text with density below the human reference of 0.80 per 1k words is not given dashes just because it "lacks" them.

When an edit is needed: write a complete sentence, or use a comma or period if the semantic relation is preserved.

> ❌ The answer is simple — focus.
> ✅ The answer is focus.

### 9. Paragraph-opening comments with no referent (downgraded: no longer auto-detected)

Formerly a rewrite rule (add "this" as a referent to a dangling paragraph opener). On 2026-10-26 it was ruled out of detection and rewriting. This feature is a weak layer-3 signal (matched retest AI 4.9% vs human 3.3%, about 1.5×, near the threshold). It belongs to the same family as the reversed layer-4 "unclear cross-sentence reference": humans are unclear 4–5× as often as AI, mostly in controllable, compact ways. AI's reading burden lies not in grammatical reference but in conceptual rewording (see rule 11). If body text has a paragraph-opening comment that reads as dangling, you may still apply "add back a referent." But do not scan for it, score it, or report it.

> Original rule 9 (a vague summary covering specific information in the same paragraph) was withdrawn on 2026-10-13. A symmetric re-check found vague summaries at net zero (vaguer 24.7% vs more specific 26.0%). Net-zero features do not enter the rewrite set. The whole rule is downgraded to X; see the X-grade list.

---

### Semantic-layer rewrite rules (rules 10–13, used with the step 1.5 results)

All four are statistically significant in the 270-pair matched retest. Synonym renaming uses a single-model criterion and is one notch weaker. Rewrites touch only items that passed item-by-item review and were included in the plan.

### 10. Synonym renaming (paragraph level)

The same entity or concept gets different substantive names within a paragraph ("optimize / enhance / upgrade / raise" rotated for one change; "footprint → base → project → node" naming one project). Readers must make an "X is Y" equivalence link. Matched retest: AI 0.83–0.86 per paragraph vs human 0.49; heavy paragraphs with ≥2 instances, AI 20.6–22.5% vs human 8.4%. **Evidence note: single-model, one-round criterion by Jev. Same direction across models but not iterated, so less robust than the other three rules.**

Fix: revert the synonym chain to the original noun. Zero information loss: the human exemplars do exactly this, repeating the original name (measured in the human corpus: one paragraph repeats the original name three times).

> ❌ The compatibility scheme could lift site utilization. (Earlier in the paragraph the same change is called "optimize" and "enhance.")
> ✅ The compatibility scheme could optimize site utilization. (Revert to the original word.)

Do not edit: different entities that happen to use near-synonyms (the criterion requires the same concept); a formal introduction of a term on first use, such as "also known as X"; literary variation in reference.

### 11. Overlong cohesion chains

Every paragraph ties tightly to the last, with zero jumps. Judgment definition: consecutive `explicit carry-over` junctions ≥6 (AI short texts median 7-link chains vs human 2; 93% of AI articles have a chain of ≥6). The real problem is not connective frequency (low on both sides, harmless) but the background probability of zero jumps: readers passively receive the whole way and never have to infer anything.

Fix: in a chain, change 1–2 junctions to natural jumps. Let the topic follow the material; do not pre-lay groundwork for the reader. Before changing a junction, check whether it carries causal or setup function. If it does, pick the next junction.

> ❌ Every paragraph opens by picking up the last paragraph's keyword ("This also explains why…," "From this angle…"), a seven-paragraph chain.
> ✅ Pick one spot and cut straight to a new topic (human exemplar: jumps from the main business straight to a quote about a new business, with no setup in between).

Do not edit: key links in an argument chain; genres that require tight linking (tutorials, legal documents).

### 12. Conclusion-cue colon (semantic-layer version)

Semantic-layer supplement to rule 2. Only the class "a clear, independent conclusion before the colon, with argument developing it after" is a true signal (AI 2.1–2.2×). Humans use more colons overall. "Empty cue leading into a list" is an order of magnitude higher in humans (X-grade).

Fix as in rule 2: delete the cue and write the content directly. If the first half continues the previous text, change only the punctuation.

### 13. Highly isomorphic triples

Three consecutive sentences share one syntactic skeleton (e.g., "What is it called? / What does it do? / Which ecosystem does it plug into?"). Broad parallelism has no discriminating power, since humans also favor parallelism. Only the **highly isomorphic** tier, where the skeleton is copied word for word, is a signal (AI 29.4% vs human 10.7%). It is a fingerprint-layer feature, with weaker evidence than layer 1.

Fix: break up one sentence by merging, splitting, reordering, or shortening it, to break the skeleton reuse. This is not deleting an item of content.

> ❌ Will the service network reach the road I drive home on for the holidays? Can the car's residual value survive scrutiny? If this company runs into trouble, who takes responsibility?
> ✅ Will the service network reach the road I drive home on for the holidays? The car's residual value: who checks it, and does it hold up? If the company runs into trouble, will it step in?

Do not edit: deliberate rhetoric (speeches, manifestos, poetry); list or table style; three-part narrative progression (what happened first, what came of it).

---

## X-grade list (never edit; prevents wrong edits)

| Feature | v1 basis | Matched retest result | Disposition |
|------|--------|--------------|------|
| Ordinal subheadings | 3.1× | **Reversed**: human 8.6% vs AI 4.9% | Never edit |
| "This means" restatement | Translationese list | **Reversed**: human 0.027 vs AI 0.016 per 1k chars | Never edit |
| Empty lead-in to list | 9.4× | **Reversed**: humans an order of magnitude higher | Never edit |
| Vague summary (not edited even with figures in the same paragraph) | Semantic layer 24.7% (one-sided count) | **Symmetric net zero**: vaguer 24.7% vs more specific 26.0%; figures retained 98% | Never edit (2026-10-13 withdrew v2 rule 9) |
| Dense precise numbers | Once suspected at 3× more in AI | δ−0.06; topic-mixing artifact | Never edit |
| Buzzword list: leverage / synergy / game-changer (Chinese study: empower / closed loop / handle) | δ+0.10 | Not significant | Never edit |
| Nominalization, similes, rhetorical questions, vague quantifiers, "first / second / in summary" | Classic lists | All \|δ\|<0.2 | Never edit |
| Uniform sentence and paragraph length | Once suspected of AI uniformity | No difference in either round (matched retest) | Do not change sentence length for rhythm |

For measured data, measurement scripts, and overturned assumptions, see [RESEARCH.md](./RESEARCH.md).

## Human review only (this skill does not touch these)

- **Metaphor fit**: real AI taste (forcing grand imagery, literal-translation stiffness, mixed metaphors), but it is neither a frequency nor a wordlist problem. Inter-model agreement is only 0–40%. The detection report may give active-metaphor density as a reference. Keep by default. Do not hand the judgment to the user. Only when the user explicitly asks for human review, list H-grade items without grading; the user decides which specific items to change.
- **Implicit metaphors and personifying metaphors**: no semantic-layer detection since 2026-10-26 (implicit-metaphor density holds only for Opus; GPT shows no difference; personification is near saturation on both sides). Merged with metaphor fit into the human-review zone: glance at them while reading the flagged zone. No candidate judgment.
- Whether three parallel examples are padding (requires semantic judgment).
- The quality of "variation": natural rhythm vs mechanical alternation of long and short. Scripts cannot tell them apart.

---

## Final checks

- Does the pre-edit report list this article's metrics, research reference and significance definition, locatable examples, concrete fixes, and exclusions, and does it wait for the user's reply before rewriting? Were A/B and semantic hits reviewed item by item, with false positives excluded? Are C/H kept within the default boundaries?
- Semantic judgments follow discipline: criteria labels only, each item judged independently, fallback label when unsure.
- Every edit maps to a plan item and rule number. Revert any edit that cannot be mapped.
- Minimal change: no drive-by polishing, no touching adjacent text.
- Every content word has a source; qualifiers and concessions ("may," "usually") are not erased.
- Structure fully preserved: heading levels, paragraph order, and positions of lists, tables, quotations, and code blocks.
- X-grade items not wrongly deleted: subheading numbering, "this means," empty lead-in list sentences.
- No manufactured variation: no sentence-length changes for rhythm, no paragraph splitting, no imposed "I" / "you."
- Em dashes handled only in high-density text.
- Vague summaries not touched, even when the same paragraph has specific values (X-grade). Rewrites must not introduce new vagueness; the information-preservation principle covers this.
- Paragraph-opening comments not scanned or scored (downgraded 2026-10-26).
- Retest and comparison report delivered to the user: A/B cleared, C metrics without large swings.
