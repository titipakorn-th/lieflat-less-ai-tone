# Detection protocol (Less AI Tone v2, step 1)

This file defines what the detection stage does and what it must not change. For rewrite rules, see [SKILL.md](./SKILL.md).

## Why detect before rewriting

Two reasons, both from measurement.

1. Most AI-tone features are **distributional** (uniform sentence length, uniform section length, avoiding word repetition). A single instance does not reveal them, and they should not be fixed one by one. Sentence-by-sentence "manufactured variation" damages the text. These features can only be decided for the whole document: either the user accepts a structure-level rewrite, or nothing changes.

2. Lesson from the first version: in one-shot rewrites, the model tends to change everything that "feels like AI tone," including features measured as not AI tone (ordinal subheadings, rhetorical questions in body text, metaphors). The result reads less human. Delivering a report with metrics, examples, and fixes first, and waiting for the user's reply before acting, is the gate against over-cleaning.

## Three-layer division of labor

Detection is not one script doing everything. Three layers each handle one part. The method comes from experiments on 430k labeling judgments.

| Layer | Covers | Who | Vehicle |
|---|---|---|---|
| Script layer | Symbol-countable items (regex hits, punctuation density, structural CV, MTLD) | detect.py | this file |
| Semantic layer | Items that need sentence meaning (synonym renaming, cohesion chains, colon classification, isomorphic triples) | the in-session model | [references/semantic-criteria.md](./references/semantic-criteria.md) |
| Human-review layer | Items where machines do not agree enough (metaphor fit, implicit metaphor, personifying metaphor) | the user | human-review zone in SKILL.md |

How the semantic layer works: the script first extracts candidates (each paragraph, each inter-paragraph junction, each colon sentence, and triples coarse-filtered by signature). The model labels each candidate against closed criteria. Regexes match only fixed surface forms and cannot catch 「同一个意思的不同写法」 (different wordings of the same meaning). A model judging "does this look like AI" brings its own bias, so the criteria must be a closed label set with independent item-by-item judgment. Holistic, feel-based scoring is not allowed.

## Commands

```bash
python3 scripts/detect.py <file or directory> [--max-hits 5] [--json]     # script layer
python3 scripts/detect.py <file> --candidates --out candidates.json        # semantic-layer candidate extraction
python3 scripts/report.py original.md revised.md before.json after.json \
    [--semantic labeled.json] --out less-ai-tone-report.md                 # default Markdown before/after report
```

Output is a graded report:

| Grade | Meaning | Rewrite policy |
|---|---|---|
| **A: mechanical fix** | Fixed sentence pattern or punctuation; the change does not touch meaning | Model reviews false positives, then proposes; edit after the user replies |
| **B: suggested fix** | Needs sentence restructuring or rewording | Model screens item by item; report typical examples and fixes; edit after the user replies |
| **C: report only** | Structure or rhythm; outside the allowlist | Do not edit by default; handle only if the user explicitly asks |
| **H: human review** | Fit the model cannot judge (personifying metaphors; metaphors and similes likewise) | Keep by default; list only if the user asks |
| **X: rejected** | Measured as not AI tone (matched retest reversed) | Never edit. Appears in the report only to prevent wrong edits |
| **F: fingerprint** | Model-specific features (em dashes, semicolons, quotation marks) | Locatable, safely rewritable hits are proposed by default. Keeping one requires a specific reason. Density is used for ranking. See the fingerprint section of SKILL.md |

## Basis for grading

Grading is based on **edit risk**, not feature strength: whether the change touches meaning, whether it requires adding information, and whether it oversteps.

- Deleting 「说白了」 ("to put it bluntly") loses no meaning → A.
- Breaking up enumeration-comma lists requires reordering components → B.
- Uniform sentence length is a whole-document property; sentence-level edits necessarily overdo it → C, notice only.
- Ordinal subheadings measured at 3.1× AI tone in round one, but the 270-pair matched retest **reversed direction** (human 8.6% vs AI 4.9%) → X. The first version listed them as rule 6 based on old data; v2 removed them.
- Vague summary was listed as v2 rule 9 at 24.7% on the semantic layer (restore the figure if the same paragraph has one). On 2026-10-13, a symmetric re-check found **net zero** (vaguer 24.7% vs more specific 26.0%) → X. The whole rule is withdrawn. Not edited even when the same paragraph has specific figures.

## Source of the X-grade list (v1 → v2 rule changes)

| v1 rule | v1 basis (629 unpaired articles) | Matched retest (270 pairs, same topic and facts) | v2 disposition |
|---|---|---|---|
| Rule 6, ordinal subheadings | AI 0.19 vs human 0.06, 3.1× | **Reversed**: human 8.6% vs AI 4.9% | Downgraded to X, not edited |
| "This means" restatement | Translationese list, 2.6–5.3× | **Reversed**: human 0.027 vs AI 0.016 per 1k chars | Downgraded to X, not edited |
| Empty lead-in to list | One of the colon-abuse cases, 9.4× | **Reversed**: humans an order of magnitude higher (normal in catalogue-style long-form) | Downgraded to X, not edited |
| Rule 8, material density | Humans 2.8× higher in number density | After matching, δ=−0.06, **no difference**. Vague summary at 24.7% was then rejected by a symmetric re-check (net zero) | Rejected again. v2 had rewritten it as "vague summary covering same-paragraph figures"; withdrawn 2026-10-13, downgraded to X |
| Rule 4, em dashes | AI 2.38 vs human 0.80, 3× | Extremes split by model: GPT −0.54 / Opus +0.95 | Downgraded to F fingerprint. Over 2 per 1k chars prioritized; low density still checked item by item |

All other v1 rules (contrast reversal, enumeration-comma lists, adjacent-sentence isomorphism, cue-phrase colons, personifying metaphors, opening formulas, and the four translationese patterns) kept their direction and magnitude under matched retest and are all retained.

## How to read the report

The script output is **candidate data**, not a conclusion for the user. After the model reviews each candidate, the pre-edit report must connect "hits in this article → research reference → examples → fixes". Review must not silently drop candidates. For layer 1 and layer 2 metrics that can be pinned to a sentence, list the raw hit count, valid hit count, to-edit count, and keep count. False positives and negative semantic judgments also get counts and reasons. If the input is a file, save item-by-item results. Whole-document distribution metrics report only measured values; do not manufacture per-sentence hit counts. Significance in the research corpus does not mean this article passed a significance test. Do not conclude from it that the author is AI.

1. **A, B, and the four semantic items**: first look at the count, density, or threshold in this article, then the human reference and matched-retest evidence. For items to be handled, give locatable original sentences and concrete fixes. Remove script false positives.
2. **X, F, and C/H**: explain the disposition of rejected features, model fingerprints, structure metrics, or metaphors. F does not infer the source model of the article. Locatable, safely rewritable hits are proposed for edit by default; keeping one requires stating what that instance does. C/H follow the whole-document metrics and human-review constraints.
3. **Check definitions**: when metric definitions or denominators differ across rounds, do not mix multipliers. Script hits for synonym rotation are heuristic only; precise judgment goes through semantic-layer synonym renaming.
4. **User reply**: stop after giving the complete set of suggestions. When the user accepts or adjusts the plan, proceed to rewriting. No item-by-item confirmation is required.

## What detection cannot do and must leave to humans

- Whether a metaphor fits (model agreement is only 0–40%; human review is the only channel). Implicit metaphors and personifying metaphors have been folded into the human-review zone since 2026-10-26; no candidate judgment.
- Whether three parallel examples are padding (narrative progression does not count; requires semantic judgment).
- Whether 「参差」 ("variation") has quality. Scripts cannot separate mechanical alternation of long and short from natural rhythm (v2.1 plans a sentence-length autocorrelation check).
- Zero-subject paragraph-opening comments are no longer detected (ruling of 2026-10-26: a weak layer-3 signal, in the same family as the reversed 「句间指代不清」 "unclear cross-sentence reference").
