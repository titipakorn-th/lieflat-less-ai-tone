# Measured features of AI-generated text (Chinese-corpus study)

> **Note on language.** The study measured Chinese text. Chinese phrases below appear as English glosses, and their numbers are Chinese-corpus numbers. The English port reuses the study's rule directions, with Chinese-only rules dropped (the "when…" temporal clause and long pre-modifier rules). Its thresholds are not calibrated for English.

This document records each rule's **assumption and measured result**, including assumptions that were overturned. A rule rests on whether its sentence pattern can be located; numbers decide only whether a pattern qualifies as a rule.

The study had two rounds: round one, a 629-article comparison (main body below), and round two, 270 matched-pair retests on the same topics and facts. Round two **overturned three round-one rules** and confirmed the direction of the rest.

## Round two: 270 matched-pair retests (basis for v2 rule changes)

Round one's core flaw was **no pairing**. AI and human articles differed in topic, facts and length, so the measured differences may reflect topic. An early case showed this: unpaired, "AI exact numbers are 3× human"; after same-fact pairing, δ fell to zero (−0.06). The whole difference came from topic.

Round-two design: 270 article pairs. Each pair shares a topic and facts (the human article's numbers and events were distilled into fact cards fed to the AI) and has aligned length. The human side has 270 articles; the AI side has GPT-5.6 ×135 and Claude Opus 4.6 ×135, **analyzed separately**. The script layer ran 90 measures with paired Wilcoxon + Cliff's δ (|δ| ≥ 0.33 significant). The semantic layer ran 9 measures plus metaphor through the structured judgment interface (Jev), covering the full set, about 430,000 judgments.

### Lesson: analyze by model

Pooled, the em-dash result was "not significant." Split by model, it was GPT −0.54 and Opus +0.95. **Two real signals in opposite directions cancelled into a false negative.** Round one's five 60-article sets had already shown this (DeepSeek 5.16, GPT 0.11), and round two confirmed it: multi-model corpora must be reported per model. v2 downgraded em dashes, semicolons, quotation marks and the attributive particle per clause to **fingerprint measures**. They report density and direction and are not universal rewrite rules (the em-dash rule triggers only above 2 per 1k characters).

### Three rules overturned (removed in v2)

| Rule | Round one | Matched retest | Conclusion |
|------|-----------|----------------|------------|
| Ordinal subheadings, 3.1× | AI 0.19 / human 0.06 | **Reversed:** human 8.6% vs AI 4.9% | The belief that "AI loves 1-2-3 numbering" is an illusion. AI's real habit is more sections, not numbering |
| "This means" restatement ("this means"), 2.6–5.3× | Listed as translationese | **Reversed:** human 0.027 vs AI 0.016 per 1k chars; reversed on all three definitions | Humans use "in other words"-style restatement more |
| Empty lead-in to list, 9.4× | One of the colon-misuse patterns | **Reversed:** humans an order of magnitude higher (0.225 vs 0.008–0.032) | A normal way to write catalog-style long-form pieces |

Also, the premise "AI lacks numbers" was overturned: no difference after pairing. But the semantic layer found the real mechanism. In 24.7% of comparable paragraphs, AI replaced the human's concrete information with abstract summary (vague summary). Rule 9 was rewritten accordingly. It no longer assumes missing numbers and only guards against a summary covering concrete values already present in the same paragraph.

**[2026-10-13 second rejection: the 24.7% was a one-sided count. Under a symmetric count, AI was vaguer in 24.7% of paragraphs and more specific in 26.0%, a net zero. 98% of numbers were retained (83% in other paragraphs of the same article, 10% written as Chinese numerals). The information-loss framing does not hold: AI differs in organization, not in information quantity. Rule 9 is withdrawn entirely and downgraded to X. Do not edit even when the same paragraph has concrete values. Rewrite fidelity is backstopped by "information conservation: every content word must have a source."]**

### Two rounds in agreement, rules retained

Contrast reversal (δ +0.88 / +0.72); dense enumeration commas (1.45×); adjacent-sentence isomorphism (1.6×; triples 2.75×); cue-phrase and conclusion colons (2.1×); personifying metaphor (1.2×, weak); zero-anaphora paragraph openings (1.5×, weak); long pre-modifier (δ +0.48 / +0.54); sentence-length and section-length variance (δ −0.88 / −0.40 and −0.91 / −0.75). Variance measures describe distribution, so editing sentence by sentence inevitably overcorrects. They enter the detection report as grade C only.

### Measures added in the semantic layer

Conclusion-cue colon (AI 2.1×; whether the text before the colon sets up a conclusion). Over-smooth cohesion (AI cross-paragraph jumps 2.1% vs human 7.2%; humans jump more often). Vague summary replacing specifics (24.7%; overturned by the symmetric recheck, see above). The first two enter the detection report; the third was withdrawn after the second review.

---

## Round one: 629-article comparison

Early on, a batch of ratios was based on 30 AI samples (sentence-length CV ×51, tripartite parallelism ×7.3, paragraph-initial ordinals 29%, em dashes as "Claude-only," and so on). Later retests on a larger corpus failed to replicate most of them, and they were discarded. See "Six measurement errors" at the end.

## Method

### Design

A controlled comparison. The same topics were written by models and compared with real articles. The dependent variable is the frequency of each construction; the independent variable is who wrote it.

Three factors must be controlled first.

**Topic and genre.** The 300 AI articles cover 38 topics, with topic range and genre aligned to the human side. If the two sides wrote different kinds of things, observed differences could not be separated from genre effects.

**Models.** Five models, 60 articles each, rather than a single model. An early version used two models and 30 articles; most of its conclusions were later overturned. For example, "em dashes are unique to Claude": expanding to five models showed DeepSeek uses them more. One model's habits can be mistaken for a shared AI trait.

**Generation conditions.** The AI side had no web access and no writing instructions, only the topic. Style instructions would hide each model's default tendencies.

### Corpus

| | Articles | Characters | Sentences | Paragraphs |
|---|---|---|---|---|
| AI | 300 | 1,179,105 | 37,642 | 14,549 |
| Human | 329 | 1,647,867 | 57,909 | 31,172 |
| Total | 629 | 2,826,972 | 95,551 | 45,721 |

Models: claude-opus-4-6, deepseek-v4-pro, gemini-3.1-pro, gpt-5.6-sol, kimi-k3, 60 each.

The human side is publicly available articles by real Chinese authors, tallied in separate groups to check whether a difference is stable within humans. A feature elevated in only one group indicates personal style or genre convention, not a shared human trait. Function words and em dashes were identified this way.

### Segmentation

Sentences: split by line first. Drop heading lines, table rows, code blocks, block quotes and list items. Then split at the Chinese sentence-final marks (equivalent to . ! ? ;), keeping fragments of four or more characters.

Dropping those lines matters. An early version split only at sentence-final marks, so Markdown tables and long lists without sentence-final punctuation counted as single sentences. One group's sentence-length standard deviation came out at 27 times its mean, which produced the claim that AI sentences are 51 times more uniform than human ones. After correction the ratio is 0.87: no difference.

Paragraphs: split on blank lines. Drop headings, tables, code blocks, quotes, list items and image lines. Keep paragraphs of eight or more characters.

### Denominators

Three, chosen by what is measured.

| Denominator | Used for | Examples |
|---|---|---|
| Per 1k characters | Lexical and punctuation features | Em dashes, enumeration commas, "not X but Y" |
| Per 100 paragraphs | Paragraph-level structure | Adjacent-sentence isomorphism, figurative openings |
| Share of same-type elements | Features bound to a structure | Interrogative subheadings as a share of all subheadings |

The wrong denominator produces a reversed conclusion. AI averages 10 subheadings per article; humans 1–2. Per 1k characters, interrogative subheadings run 32× higher. As a share of subheadings, AI is 2.7% and the human maximum 3.6%, and the difference vanishes. The former measures "AI has many subheadings"; the latter measures the actual preference, "AI likes to use questions as subheadings."

Paragraph-initial features use non-initial paragraphs as the denominator, since an opening paragraph has no preceding text to refer back to.

### Decision criteria

*R* = generated frequency ÷ human frequency.

| *R* | Decision |
|---|---|
| ≥ 2.0 | Include as a rule |
| 1.25 – 2.0 | Include only with stable human groups and sufficient volume |
| 0.8 – 1.25 | No difference; exclude |
| < 0.8 | Humans use it more; the reverse is not grounds for deletion |

Three further conditions apply beyond the ratio.

**Cross-group stability.** Values across human groups must not differ by more than 5×. Em dashes differ about 100-fold between groups (minimum 0.01, maximum 1.29), so despite *R* = 3.0 the rule carries an explicit caveat.

**Locatable trigger.** A rule must identify which sentence and which word to change. "Reads too uniform" cannot be verified and is excluded. Discourse-level judgments, such as whether a metaphor fits or whether three parallel cases are padding, are excluded too, however much they subjectively resemble AI tone.

**Rewrite compatible with the whitelist.** Material density was 2.8× higher among humans, but "add numbers" violates information conservation. v2 narrowed the rule to "do not let a summary replace existing concrete data." That narrower version was withdrawn on 2026-10-13 along with the symmetric-count rejection: a net-zero feature does not enter the rewrite set. Function words are likewise used less by AI, but "add function words" cannot be verified, so the rule was abandoned.

### Operators

Each rule has one regex, defined at the top of its script and open to modification.

This is the thinnest part of the method. Regexes match literal form, not meaning; written too broadly, they capture material that should not count. This project got it wrong six times (see below). The resulting operating requirement: **before changing a rule, sample 20 matched instances, then look at the frequency.**

### Reproducibility

The corpus is not included (copyright and privacy), so third parties cannot verify the figures below. What can be reused is the method and the scripts. Substituting your own corpus yields the corresponding figures for it.

This is a substantive defect, not a disclaimer. Figures that cannot be checked leave readers only the choice to trust them or not. What can be examined is the segmentation rules, denominator choices, decision thresholds and operator definitions, all published in the scripts.

## Assumption vs. measurement

The ratio column is always generated ÷ human. Above 1 means generated text uses the feature more, which is the precondition for treating it as an AI trace.

### Confirmed and adopted as rules (round one)

| Feature | Assumption | Measured | *R* | Rule |
|---|---|---|---|---|
| Zero-anaphora paragraph opening | Not assumed; raised during use | Generated 0.61%, human 0.14% (share of non-initial paragraphs) | 4.4× | 11 |
| Personifying vehicle | "Metaphor wraps abstract concepts" | Generated 0.018, human 0.002 | 7.3× | 7 |
| Colon overuse (cue phrase) | "Feels templated" | Generated 0.29, human 0.08 | 3.8× | 5 |
| Colon overuse (empty lead-in to list) | Not assumed | Generated 0.29, human 0.03 | 9.4× | 5 |
| Contrast reversal | "Models love the not-X-but-Y construction" | Generated 0.73, human 0.22 | 3.4× | 1 |
| Em dash | "Unique to Claude, ×3" | Generated 2.38, human 0.80 | 3.0× | 4 |
| Opening formula ("to put it bluntly") | Not quantified | Generated 0.025, human 0.008 | 3.2× | 9 |
| Ordinal as subheading | "29% of GPT paragraphs use ordinals" | Generated 0.19, human 0.06 | 3.1× | 6 |
| Material density (missing figures) | Not assumed | Numerals: generated 6.34, human 17.92 | 0.35× (human 2.8× higher) | 8 |
| Adjacent-sentence isomorphism | Assumed "tripartite parallelism ×7" | Per 100 paragraphs: generated 9.41, human 4.81 | 2.0× | 3 |
| Dense enumeration commas | Same as above | Generated 3.21, human 1.78 | 1.8× | 2 |
| Translationese, five forms | "Retains English syntax," 18 forms | Only 5 qualify (see below) | 2.6–5.3× | 10 |

### Not confirmed, removed

| Feature | Assumption | Measured | *R* | Conclusion |
|---|---|---|---|---|
| Sentence-length uniformity | "AI is 50× more uniform" | Sentence-length CV: generated 0.58, human 0.67 | 0.87× | The ×51 came from a sentence-splitting defect |
| Adjacent sentence-length difference | Same as above | Generated 21.7, human 21.7 | 1.00× | No difference at all |
| Paragraph-length uniformity | "AI paragraphs are also highly uniform" | Robust dispersion: generated 0.94, human 1.00 | 0.94× | The 3.9× CV came from one unbroken 19,335-character paragraph |
| Monosyllabic particles (jiu, hen, le) | "Humans 3–7× higher" | "jiu": generated 2.93, human 6.45 | 0.45× | The direction is addition, not deletion; human groups vary, and one group alone can inflate the ratio |
| Colloquial connectives | "Humans 3–6× higher" | Generated 1.01, human 3.87 | 0.26× | Same as above |
| Fewer pronouns, repeated full names | "AI repeats full names" | Same noun opening adjacent sentences: generated 0.02, human 0.04 | 0.5× | Humans do it more |
| Passive voice | "AI retains English passives" | Abstract passive: generated 0.09 | — | Far below threshold; human 3.2% vs generated 4.5%, also no difference |
| Self-answering questions | "Especially common in Claude" | Generated 0.13, human 0.13 | 1.03× | Reversed across three rounds of measurement (see below) |
| Interrogative subheadings | "AI uses questions as scaffolding" | Share of subheadings: generated 2.7%, human max 3.6% | 0.75× | 32× per 1k characters was a denominator trap |
| In-body questions | Same as above | Generated 0.10, human 1.83 | 0.05× | Humans 17× higher; deleting them would read less human |
| Intra-sentence parallelism | "Tripartite parallelism, GPT ×7.3" | Two items sharing an opening character: generated 2.35, human 3.87 | 0.61× | Humans higher within sentences; only cross-sentence repetition holds |
| Metaphor as such | "Non-fiction should avoid figurative language" | Metaphor markers: generated 0.16, human 0.38 | 0.42× | Humans 2.4× higher; metaphor as a standalone paragraph 8× |
| Abstract noun with concrete verb | "time keeps the details, anxiety takes shape" | Generated 0.001, human 0.001 | 0.7× | Neither side writes it |
| Verb nominalization | "completed the optimization of…" (light-verb frame) | Generated 0.003, human 0.005 | 0.52× | Humans higher; measured with abstract suffixes instead, generated is 1.6× higher |
| In-body ordinals | "GPT 29% vs human 4%" | Sentence-initial "first, …": generated 0.06, human 0.03 | 2× | Weakest form; mid-sentence "first, …" at 1.2× shows no difference |

### Colons: meaningful only when split by function

A small group of human articles (mostly interview format) uses colons far more than the rest. They account for 77% of all human colons and would dominate any total. The table below excludes that group; the human side is then 189 articles.

Total colon density is 5.30 per 1k characters for generated text and 3.65 for human, a ratio of 1.45. But the two human groups sit at 2.39 and 6.05, one of them above the generated side. Internal variation approaches the human–machine gap, so the total cannot serve as a criterion. Split by function:

| Function | Generated | Human | *R* | G1 | G2 | Spread | Decision |
|---|---|---|---|---|---|---|---|
| Cue phrase ("the core is:") | 0.29 | 0.08 | 3.78× | 0.06 | 0.11 | 1.8× | Include |
| Empty lead-in to list ("several scenarios:") | 0.29 | 0.03 | 9.38× | 0.03 | 0.03 | 1.1× | Include |
| Mid-sentence general-then-specific (followed by Chinese characters) | 3.00 | 1.80 | 1.66× | 0.61 | 4.07 | 6.6× | Inconsistent across groups |
| Bold subheading + colon | 0.43 | 0.26 | 1.66× | 0.10 | 0.56 | 5.7× | Inconsistent across groups |
| Introducing items (followed by numbering) | 0.87 | 0.62 | 1.40× | 0.80 | 0.27 | 2.9× | Difference insufficient |
| Definitional (noun + colon) | 1.34 | 0.98 | 1.38× | 0.67 | 1.56 | 2.3× | Difference insufficient |
| Quotation (speech verb / speaker) | 1.44 | 1.54 | 0.93× | 0.93 | 2.71 | 2.9× | No difference |

Only the first two meet both conditions: a sufficient ratio, and near-zero values in both human groups. That combination makes "humans essentially do not write this way" a stable basis for attributing a given colon.

**The mid-sentence general-then-specific pattern cannot be measured.** The 1.66× ratio looks like a difference, but the human groups sit at 0.61 and 4.07, a 6.6-fold spread. One writer barely uses the pattern; another uses it more than the generated side. Given one such colon, its origin cannot be determined. Excluding instances with quotation cues leaves a 6.8× spread, so quotation structure is not the cause.

This pattern is also a legitimate colon use under GB/T 15834, the Chinese national punctuation standard (after a general statement, introducing its specifics). Replacing it with a comma loses the hierarchy; replacing it with a period severs the correspondence. It is therefore explicitly excluded from edits.

**Subheading colons are a denominator trap.** Per 1k characters, the figures are 1.07 for AI and 0.07 for human, a ratio of 15.7. But the generated side has six times as many subheadings in total. As a share of subheadings: 41.6% vs 24.1%, a ratio of only 1.7. The human groups range from 7.7% to 62.1%, and one exceeds the generated side. As with interrogative subheadings, not included.

Quotation colons account for 41–45% of human colons against 27.6% for generated text. The two sides distribute colon functions differently, but absolute quotation volume is level (0.93×).

## Paragraph-level structure

The denominator is paragraph count, not character count.

```
# Script deleted in the English port. The isomorphism metrics live on in detect.py and compare-human-ai.py.
python3 scripts/check-structure.py --human <dirs...> --ai <dirs...>
```

| Metric | Generated | Human | *R* | Human-side stability |
|---|---|---|---|---|
| Two adjacent sentences isomorphic (per 100 paragraphs) | 9.41 | 4.81 | **1.96×** | Stable |
| Three adjacent sentences isomorphic (per 100 paragraphs) | 0.84 | 0.41 | **2.03×** | Stable |
| Zero-anaphora paragraph opening (zero-subject comment; share of non-initial paragraphs) | 0.61% | 0.14% | **4.38×** | Stable |
| Figurative paragraph opening (per 100 paragraphs; control) | 0.03 | 0.21 | 0.13× | Varies widely |

Total paragraph-initial connective density shows no difference (generated 14.4%, human 15.1%). Generated text does not use fewer connectives. Its evaluative sentences omit the anaphoric element; adding a single demonstrative ("this") restores the link.

Intra-sentence and cross-sentence patterns must be assessed separately. Humans use intra-sentence parallelism at least as much as generated text does:

| Intra-sentence form | Generated | Human | *R* |
|---|---|---|---|
| Two items sharing an opening (repeated "must… must…" frame) | 2.35 | 3.87 | 0.61× |
| Three items sharing an opening | 0.34 | 0.36 | 0.95× |
| Repeated "more X, more X" frame | 0.13 | 0.15 | 0.84× |
| Parallel "X's A, Y's B, Z's C" frame | 0.14 | 0.12 | 1.10× |

Hence rule 3 covers cross-sentence repetition only. Intra-sentence parallelism is kept.

Metaphor as a standalone paragraph is 8× higher among humans (0.43 in one group). When such a paragraph reads awkwardly, the cause is usually a missing anaphor, not the metaphor itself.

Case stacking raises two questions with opposite answers. On density, generated text is genuinely higher: paragraphs containing a "proper noun + action" case sentence are 9.11% of generated paragraphs vs 3.13% of human ones, 3–4× across all counts. But the claim that models specifically favor three cases does not hold:

| Cases in paragraph | Generated | Human |
|---|---|---|
| Exactly 1 | 91.0% | 92.6% |
| Exactly 2 | 8.4% | 6.5% |
| Exactly 3 | 0.6% | 0.5% |
| 4 or more | 0.0% | 0.4% |

The conditional distributions are nearly identical. Generated text simply has about 3× as many case sentences overall, and three-case paragraphs rise with them; there is no preference for the number three. Sampling the generated three-case paragraphs shows most are narrative progression (what happened, how it was done, what resulted), which is ordinary writing. Rule 3 therefore treats this layer as guidance rather than a hard rule.

## Translationese: 18 narrowed to 5

```
# Script deleted in the English port. The table below is the Chinese-corpus record.
python3 scripts/check-translationese.py <generated corpus dirs...>
```

| Construction | Generated per 1k chars | Coverage | Decision |
|---|---|---|---|
| Long pre-modifier | 0.42 | 179/300 | Include |
| "When… , at that time" temporal clause | 0.26 | 136/300 | Include |
| Topic-shell frame (fronted topic wrapper) | 0.22 | 137/300 | Include |
| Sentence-initial connective | 0.18 | 102/300 | Include |
| "This means" | 0.15 | 122/300 | Include |
| Abstract passive | 0.09 | 75/300 | Drop |
| "in the course of…" | 0.07 | 64/300 | Drop |
| "not merely" | 0.05 | 41/300 | Drop |
| "exists / has" verb frame | 0.04 | 29/300 | Drop |
| Light verb ("carried out … analysis") | 0.03 | 30/300 | Drop |
| "causes… to be able to" | 0.03 | 26/300 | Drop |
| "to some degree" (literal degree phrase) | 0.02 | 25/300 | Drop |
| "play the role of" | 0.02 | 22/300 | Drop |
| "it is worth noting that" (formal subject) | 0.02 | 19/300 | Drop |
| "if… then" frame | 0.01 | 9/300 | Drop |
| "in a… manner" frame | 0.01 | 8/300 | Drop |
| "a series of" (literal plural) | 0.00 | 5/300 | Drop |
| "receive attention from…" | 0.00 | 4/300 | Drop |

The five retained constructions show AI-to-human ratios of 2.6 to 5.3×. The thirteen dropped fall below 0.09 per 1k characters. They are translationese, but not AI traces: modern written Chinese already uses them.

Three of the dropped items were in the original version of the rule set ("in a… manner", "causes… to be able to", "play the role of"). All measure below 0.03, so they were removed together.

## Between-model variation

A single feature can differ by an order of magnitude between models. Do not judge by "a given model's flavor."

| Feature | Claude | DeepSeek | Gemini | GPT | Kimi |
|------|--------|----------|--------|-----|------|
| Em dash | 4.25 | **5.16** | 0.51 | 0.11 | 2.32 |
| Cue colon | 0.38 | **0.43** | 0.22 | 0.25 | 0.32 |
| Contrast reversal (not X but Y) | 0.61 | 0.86 | 0.29 | **1.26** | 0.51 |
| Ordinal subheading | **1.00** | 0.69 | 0.22 | 0.73 | 0.82 |
| Long pre-modifier | 0.64 | **0.65** | 0.48 | 0.06 | 0.22 |
| Interrogative subheading | 0.043 | 0.086 | **0.173** | 0.008 | 0.000 |

DeepSeek, not Claude, leads on em dashes, and GPT barely uses them. Cue colons peak in DeepSeek and Claude, not Gemini; the earlier attribution to Gemini came from an over-broad regex.

GPT's em-dash rate of 0.11 has led some to argue the feature is no longer an AI trace. But Claude runs more than 5× the human rate, and Claude is widely used for writing, so the rule stays.

## Six measurement errors

Each came from applying a broad regex to a precisely defined rule, or from choosing the wrong denominator. Each happened because the frequency was read before the matches were inspected.

1. **Long pre-modifier 3.04 per 1k.** The regex counted ordinary sentences such as "quality management is the most overlooked problem in the zero-to-one stage" as long modifiers. After tightening: 0.35.
2. **Coordinating conjunctions 0.26.** The rule says "two or more within one clause," but the operator measured single occurrences of the coordinators "and also" and "and". Measured per the rule: 0.00.
3. **Nested "of… of… of…" modifiers 0.25.** The regex matched across enumeration commas, counting ordinary lists such as "Brazil's LGPD, India's DPDPA, Japan's APPI" as nested modifiers. After tightening: 0.06.
4. **Cue colon 5.97 vs 5.45, "no difference."** The operator was "CJK character + colon." Of 6,431 matches, 1,266 were headings, 1,225 list items and 207 dialogue, all explicitly exempt under the rule. Measured per the definition: 0.32 vs 0.08.
5. **Interrogative subheadings 32×.** The denominator was characters, but AI averages 10 subheadings per article against 1–2 for humans. As a share of subheadings: 2.7% vs a human maximum of 3.6%, no difference.
6. **Metaphor packaging 0.000.** The operator was a hard-coded list of 11 words ("warehouse," "drawer," "temperature," "key" …), but actual metaphors such as "like a building's access control" contain none of them. Measured as a construction, humans are 2.4× higher, the reverse of the hypothesis.

The working requirement that follows: **inspect 20 matched instances before reading the frequency.** For measures involving structural elements (subheadings, paragraphs, lists), the denominator must be the total count of that same element type.

## Limitations

1. **The human corpus is limited.** Internal variation is already large (em dashes differ 100-fold; function-word density differs 3-fold). Expanding the corpus may change conclusions again.
2. **Some parts have no human comparison.** For AI-side-only measures, the results give absolute frequencies. A construction's high frequency in AI text does not mean humans never write it.
3. **Regex approximations.** Discourse-level features cannot be expressed as regexes and fall back to locatable form. Known unmeasurable items: whether a question addresses a genuine gap, whether three cases are parallel, whether a metaphor is apt, and whether a metaphor merely restates the preceding paragraph. These require human reading. Do not write them into rules because they "feel like AI."
4. **Topics are not matched.** The AI articles came from one batch of topics; the human articles span years and subjects. Some differences may reflect topic rather than style.
5. **Denominators are not uniform.** Article structure affects the per-1k-character denominator, so features involving structural elements need particular care.
6. **Figures have a shelf life.** Each model update moves toward human style. GPT's em-dash rate went from "nearly one per sentence" to 0.11 in under a year.

## Measuring it yourself

The figures above come from a corpus that is not included, so they cannot be verified directly. The method transfers: rerun it on your own corpus.

```bash
# Sentence level and structure: per-metric comparison of human vs. AI, all detect.py metrics
python3 scripts/compare-human-ai.py --human <human corpus dirs...> --ai <AI corpus dirs...>

# Smoke test for detection patterns
python3 scripts/test_detect.py
```

The paragraph-level script (`check-structure.py`) and the translationese script (`check-translationese.py`) were deleted in the English port. Isomorphism measures are now in `detect.py`; the topic-shell and sentence-initial connective forms are covered by the Stock framing rule.

The scripts take corpus directories as arguments and do not use directory names as labels, since corpus directories often carry source information that could leak into the output. Operator definitions sit at the top of each script and can be edited directly.

When changing a rule, look at what the regex actually matches before looking at the number.

## Appendix: sources for v2.1 detection-layer reference values

Each hard-coded value in `detect.py`'s `HUMAN_REF` and in the human reference column of `report.py` has the source below. A reference value is the median of each side in the 270-pair matched retest (the paired-metrics CSV, Wilcoxon + Cliff's δ, split by model).

| Detection-report measure | Human median | AI median | Experimental basis | Notes |
|---|---|---|---|---|
| Contrast reversal (not A but B) | 0.22 | 0.94 | Same regex; Europeanized-construction sub-item | δ +0.88 (GPT) / +0.72 (Opus); same direction in both rounds |
| Cue-phrase colon | 0.08 | — | Semantic layer, "conclusion-cue" tier, AI 2.1× | Script-level colon density is higher in humans (−0.37 / −0.31); only the conclusion-cue tier is a signal |
| Enumeration comma list ≥3 | 1.78 | — | Round-one value; matched-retest dense enumeration AI 1.45× (7.845 vs 5.398) | **Basis differs:** the experiment counts total enumeration-comma density; detect counts ≥3-item list hits. Magnitudes are not directly comparable |
| Sentence-length CV | 0.54 | 0.46 | Matched-retest sentence-length variation | **Differs from v1 threshold note:** v1 README cited 0.67 (sample measurement); v2.1 uses the matched-round 0.54 |
| Section-length CV | 0.83 | 0.31 | Matched-retest section-length variation | δ −0.91 / −0.75 |
| Headings per 1k chars | 0.32 | 1.26 | Matched-retest heading density | Human median: one article with 0–1 headings |
| MTLD (rough) | 143 | 227 | Experimental mtld (AI 227 / human 143) | **Basis differs:** detect uses a two-character pseudo-word approximation, so absolute values are not comparable with the experiment's mtld scale. Use only for longitudinal comparison within the same corpus |
| Em dash per 1k chars | 0.83 | 2.02 | Matched retest | **Fingerprints not pooled:** GPT −0.54 / Opus +0.95 point in opposite directions. The AI column is a pooled reference only; rewriting judges by model-specific direction |
| Semicolon per 1k chars | 0.77 | 1.51 | Same | GPT-specific, δ +0.80 |
| Quotation marks per 1k chars | — | — | Opus lower, δ −0.67 | Strong individual variation in density; reported only, not judged |
| Isomorphic pairs per 100 paragraphs | 4.81 | 8.71 | Broad signature | Highly isomorphic tier AI 8.71% vs 5.52% (1.6×). Detect uses the broad form for coarse screening; the semantic layer makes the precise judgment |
| Isomorphic triples per 100 paragraphs | 0.41 | 0.84 | Broad signature | Triples 2.75×; after coarse screening, the semantic layer judges "highly isomorphic" |

Semantic-layer thresholds (summary basis):

| Summary measure | Threshold | Experimental basis |
|---|---|---|
| Synonym renaming | ≥ 0.7 per paragraph, or heavy-hit paragraphs (≥ 2 groups) > 15% | AI 0.83–0.86 per paragraph vs human 0.49; heavy-hit paragraphs 20.6–22.5% vs 8.4% (single-model Jev run; weaker than the other three) |
| Cohesion chain | Longest chain ≥ 6 | AI short-article median 7 vs human 2; AI accounts for 93% of articles with chains ≥ 6 |
| Conclusion-cue colon | Any hit reported | Conclusion-cue tier AI 2.1×; quotation, layout, definition and empty-cue tiers are not signals (empty cue reversed) |
| Highly isomorphic triple | ≥ 2 groups | Highly isomorphic triples AI 29.4% vs human 10.7% |

**Pending calibration:** σ (the human distribution's standard deviation) was not measured, so the P_H percentile scale cannot yet be computed; the experiment has only medians. The sentence-length CV discrepancy (0.54 vs 0.67) and the enumeration-comma and MTLD basis differences will be unified after the next matched-pair corpus is retested.

---

**Rule set** [SKILL.md](./SKILL.md) · **Overview** [README.md](./README.md)
