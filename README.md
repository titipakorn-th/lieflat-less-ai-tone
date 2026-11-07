# Lieflat Less AI Tone

![Lieflat Less AI Tone: 5.2M characters, 100+ measures, approximately 500K model semantic judgments](assets/less-ai-tone-hero-en.png)

**A post-draft "less AI tone" skill for Chinese writing, built on two rounds of measurement: 1,169 articles, about 5.2 million Chinese characters, 100+ measures, and about 500,000 model semantic judgments.** It reports what it finds, with research benchmarks, cited passages from your draft, and proposed edits. It rewrites and rechecks only after you reply.

## 1 Research question

Even as AI's coding has improved, its Chinese prose often still reads oddly. Many strong models produce long pieces that readers have to reread several times. A main cause is the constant use of contrasts like 「不是技术问题，而是认知问题」 (“not a technical problem but a cognitive one”), dense em dashes and semicolons, and metaphors that are hard to follow.

Common fixes are a banned-word list or a "remove AI tone" prompt. In practice both have clear limits:

- **Word lists miss the real signal.** Many texts avoid 赋能 (empower), 闭环 (closed loop) and 抓手 (handle) and keep punctuation restrained, yet still read as AI-written after three paragraphs.
- **Bulk rules cause over-editing.** Given a dozen rules, a model edits aggressively: it deletes natural rhetorical questions and 一、二、三 numbered headings, and splits fluent sentences to satisfy "vary sentence length."

Popular "AI tone checklists" mostly come from anecdotes and personal taste and have never been tested systematically. This project starts from the hard-to-verify sense that text "reads like AI," finds measures that objectively reflect model writing habits, quantifies them, and only then writes rules.

Making this a reliable skill comes down to three questions:

1. How do we measure AI tone accurately when scripts cannot count it? This determines whether deeper habits in sentence meaning and context get caught.
2. Which linguistic features actually affect reading? This determines where rewrite rules should aim.
3. How do we keep the model in check? This determines whether rewriting removes formulaic patterns without damaging normal expression.

Two principles guide the design:

- **Validity:** each measure maps to one locatable syntactic or discourse problem, so a high or low value points to a specific rule.
- **Reliability:** evaluation and before/after changes are quantified, so edits are not based on feel.

## 2 Two rounds of experiments

### 2.1 Round one: 629 comparison articles

Generation: the same topics; five models wrote 60 articles each (300 total), compared with 329 human-written articles. Models: claude-opus-4-6, deepseek-v4-pro, gemini-3.1-pro, gpt-5.6-sol, kimi-k3. Human groups were tallied separately to test cross-group consistency.

| Side | Articles | Characters | Sentences | Paragraphs |
|---|---|---|---|---|
| Generated | 300 | 1,179,105 | 37,642 | 14,549 |
| Human | 329 | 1,647,867 | 57,909 | 31,172 |

**Criteria.** Ratio R = generated frequency ÷ human frequency. R ≥ 2.0 is included; 1.25–2.0 is included conditionally (requires consistency across human groups and sufficient volume); 0.8–1.25 is excluded; below 0.8, humans use the feature more, and the reverse is not grounds for deletion. Three further conditions apply: cross-group consistency (range ≤ 5×), operator locatability (can point to the sentence to change), and actionability (a rule like "add function words" cannot be verified, so it was dropped).

### 2.2 Round two: 270 matched-pair retests

Round one's core flaw was that its corpora were not matched. Round two fixed this: facts and figures from each human article were distilled into a task card, and the model wrote on the same topic under the same factual constraints, with aligned length. GPT-5.6 wrote 135 articles and Claude Opus 4.6 wrote 135; the two models were analyzed separately.

| Layer | Tool | What it measures | Scale |
|---|---|---|---|
| Script | Python regex + statistics | 90 countable measures: punctuation density, sentence-length distribution, lexical diversity (mtld/mattr), Europeanized constructions, section geometry, paragraph bridging, formality variation, four-character idioms, blacklisted words | All 540 round-two articles; paired Wilcoxon + Cliff's δ; \|δ\| ≥ 0.33 significant |
| Semantic | Structured judgment interface (Jev) | 9 measures scripts cannot assess: conclusion-cue colon, dense enumeration, ordinal subheadings, adjacent-sentence isomorphism, zero-anaphora paragraph openings, cross-sentence and cross-paragraph cohesion, "This means" restatement, vague summaries replacing specifics, personifying metaphors; plus active metaphor density | About 500,000 judgments (431,000 in round two plus about 110,000 in a supplementary round on anaphora and synonym renaming); 19,200 requests; 354 million tokens; all saved for recomputation |
| Human | Sentence-level annotation + sample review | Metaphor aptness; error rate of the criteria | Failure patterns of AI metaphors: forced grand imagery, translated phrasing, mixed metaphors, triple-part titles |

The 500,000 judgments describe the **research**, not the number of model calls needed to check one new draft. In ordinary use, the scripts extract candidates and the in-session model assesses them against the closed criteria in [references/semantic-criteria.md](./references/semantic-criteria.md).

## 3 Core results

Results are sorted into tiers by strength of evidence. Each table shows round-one values and round-two matched-retest results, labeled by basis. Script-layer retests use paired Wilcoxon + Cliff's δ (|δ| ≥ 0.33 significant); semantic-layer results come from about 500,000 model judgments.

**What δ means.** Take a random AI article and a random human article and compare them: δ = P(AI has more) − P(AI has fewer). Positive means AI uses more than humans; negative, fewer. Larger absolute values mean larger gaps: |δ| ≥ 0.33 is significant, and ≥ 0.66 is a large gap.

### 3.1 Tier 1: general AI-tone measures

Nine measures, found by the script, semantic and human layers, that are significant in the same direction for both GPT-5.6 and Opus 4.6:

| Measure | Script evidence (GPT δ / Opus δ) | Semantic evidence | Direction |
|---|---|---|---|
| **Contrast reversal 「不是……而是……」** (“not X but Y”) | +0.88 / +0.72 (strongest pure-writing signal) | Dense enumeration 1.45× | More in generated text. Examples: 「用户购买的不是模型参数，而是一件每天要戴、需要充电、还会出现在社交场合的物品」「潘宇扬并不是从通用AI退回一个小功能，而是在尝试证明另一种生长顺序」 |
| **Avoids word repetition (mtld/mattr)** | +0.91 / +0.55; +0.75 / +0.55 | — | Generated text has more varied vocabulary. Example: 「优化／增强／提升／提高」 (optimize / enhance / raise / improve) rotate within one paragraph. Humans repeat the same term; AI rotates synonyms, as in 「采用兼容体系……站点利用率就可能提升」 |
| **Over-fragmented sections** | Section-length variance −0.91 / −0.75; headings per 1k chars +0.65 / +0.83; sentences per section −0.63 / −0.79; section count +0.51 / +0.70 (median AI 7 vs human 1) | — (section structure is purely structural; the semantic layer does not test it) | More, shorter, more uniform sections in generated text. Sample: AI articles run 1.3–1.7 headings per 1k chars (3,000–6,000-character articles split into 5–9 sections); humans write continuously and change paragraphs at natural topic shifts |
| **Sentence length and rhythm too uniform** | Sentence-length variance −0.88 / −0.40; comma-clause length variance −0.87 (GPT) | — | Generated sentence lengths vary less. Round-one sampling: AI sentence-length CV 0.41–0.55 vs human 0.67; the matched-retest human reference is 0.54. The two rounds are not directly comparable, and this does not justify mechanically adjusting sentence length |
| **Long pre-modifier (Europeanized)** | +0.48 / +0.54 | — | More long modifiers before nouns. Examples: 「它还不是一套能够在任何餐桌上完全自动运行的系统」「这种连续数据也解释了为什么团队没有把产品做成一次拍照识别的工具」 (twenty-odd characters of modifier before the head noun) |
| **Conclusion-cue colon** | Total colon density is higher in humans (−0.37 / −0.31) | Conclusion-cue colons 2.1× AI (「核心是：」 "the core is:", 「残酷的现实是：」 "the harsh reality is:") | Generated text tends to state the conclusion first. Example: 「这组数字传递出一个残酷的现实：不管你是街边个体户的夫妻店……三个月是第一道坎，半年是生死线」 |
| **Over-smooth cohesion** | — | Explicit carry-over: AI 98.9% vs human 95.2%. Cross-paragraph jumps: AI 2.1% vs human 7.2% | Generated paragraphs connect too tightly. Example: consecutive paragraphs open with 「这也解释了为什么……」「从这个角度看……」 (in 30 articles, 「这也解释了」 opened a paragraph 10 times). Humans jump to a new topic about once every 14 paragraphs; AI about once every 50 |
| **Dense enumeration** | Enumeration comma +0.56 (GPT); semicolon +0.80 (GPT) | AI 7.845 vs human 5.398 per 1k chars (1.45×) | More parallel lists in generated text. Example: 「火锅、快餐、家庭聚餐和独自进食，不同光线、不同穿着、……」 (one sentence strings several scene dimensions together) |
| **Poor metaphor aptness** | — (regex counts only metaphor markers, which are 2.4× more frequent in humans) | — (six models agreed pairwise only 0–40%; in the highest-scoring paragraph, 9 of 22 sentences were false positives. This reflects a gap in model judgment, not the absence of signal) | **Confirmed by human review.** Failure patterns: forced grand imagery (「窄门」 narrow gate, 「三根支柱」 three pillars); translated phrasing (「钢夹」 steel clamp); mixed metaphors (「坠崖＋松动地板」 falling off a cliff plus a loose floorboard); triple-part titles. Aptness can only be judged by humans, so the skill keeps original metaphors by default |

**One important second rejection.** The first semantic test found that 24.7% of comparable paragraphs became more abstract than their source, and a rewrite rule was set on that basis. A symmetric recheck found 26.0% moving in the opposite direction, a net difference near zero; exact numeric density also showed no difference in the matched retest. "Vague summary" was therefore downgraded from a rewrite rule to grade X and no longer drives edits. Source facts and qualifiers remain protected by information conservation.

### 3.2 Tier 2: model-specific traits

These are highly repetitive surface habits: punctuation and syntax preferences such as how many em dashes a model uses, how long its sentences run, and whether it uses semicolons. Evidence comes mainly from script checks.

| Trait | GPT-5.6 | Claude Opus 4.6 | Meaning |
|---|---|---|---|
| Em dash | −0.54 (fewer than humans) | **+0.95** (used in 100% of articles) | Opposite directions, so a rewrite must first establish which model the text resembles. Opus example: 「在营收急剧收缩的压力下，公司迅速启动了大规模的营销开支削减——最先被砍掉的，正是搜索广告和效果投放」 |
| 「的」 per clause | −0.75 | +0.62 | GPT uses 「的」 less than humans; Opus uses more. Opposite directions |
| Quotation marks | ≈0 | −0.67 | Opus rarely uses quotation marks, far fewer than humans |
| Semicolon / enumeration comma | +0.80 / +0.56 | −0.11 / +0.14 | GPT-specific. Example: 「对于食材分明的欧美常见"白人餐"，准确率可以超过90%；到了中餐火锅，准确率约为70%至80%；遇到糊状食物，则需要用户通过语音或事后手动补充」: three scenario tiers strung together with two semicolons; humans more often split them into three sentences |
| Sentence structure (fewer single-verb sentences, etc.) | All significant | None significant | GPT-specific, with three sub-traits. **① Fewer single-verb sentences** (δ −0.72): short sentences where one verb carries the whole sentence (「转折发生在疫情期间。」「Odyss试图把这一步交给机器。」) are rare; verbs stack instead, as in 「项链利用多模态视觉大模型，观察食物被送入口中的过程，再把零散的进食动作还原成一天的饮食记录」 (four verbs in one sentence). **② Fewer static sentences** (δ −0.71): statements of state or judgment (「问题在于，开发者影响力不等于消费者入口。」) are common in humans; GPT writes almost everything as process. **③ Shorter subject–predicate distance** (δ −0.62): humans often insert a long stretch between subject and predicate (「续航能否覆盖一天，设备是否舒适，记录是否准确，建议是否真的改变饮食，这些问题只有在持续使用中才会显现」, about 30 characters before the predicate); GPT rarely does this |
| Fewer questions | −0.59 | −0.12 | GPT asks far fewer questions than humans; Opus is close to humans |
| Long vs. medium sentences | −0.68 / +0.81 | +0.05 / +0.04 | GPT has fewer long sentences and more medium ones. Lengths cluster at 25–45 characters, with almost no short 6–12-character closers and very few run-ons over 60 characters |
| Late-placed focus | +0.05 | +0.47 | Opus-specific: new information goes at the end of the sentence, after setup. Examples: 「定价权不在工厂手里，品牌归属也不在工厂手里，工厂只是全球供应链上那个沉默的、可以被随时替换的生产节点」「如果说一个行业每天有近一万间门店关门，听起来像是危言耸听，但这恰恰是中国餐饮业正在发生的事」: readers wait until the last clause to learn the point |
| **Active metaphor density** | 2.099 ≈ human 2.066 | **2.851** (the pooled 1.2× is entirely driven by Opus) | An Opus-specific research observation, not a general editing basis. GPT's metaphor count matches humans. For both models, metaphor aptness needs human review; the skill keeps original metaphors by default |

### 3.3 Tier 3: measures that are not significant

| Measure | Evidence |
|---|---|
| Zero-anaphora paragraph openings (zero-subject comments) | AI 4.9% vs human 3.3% (about 1.5×) |
| Highly isomorphic adjacent sentences | AI 8.71% vs 5.52% (1.6×; triples 2.75×) |
| Dense exact numbers in AI text | δ −0.06; a topic-mixing artifact that disappears after pairing |
| Buzzwords: 赋能 (empower), 闭环 (closed loop), 抓手 (handle) | δ +0.10; no difference after pairing on matched facts |
| 「首先/其次/总之」 (first / second / in sum) connectives | δ +0.02; no longer works at all on current models |
| 「这意味着」-style "This means" restatement | Humans use it more (reversed on all three measures) |

## 4 Workflow

```bash
# Step 1: script detection (report only, no rewriting; --json saves results for step 4)
python3 scripts/detect.py <file or directory> --json > /tmp/before.json

# Step 1.5: semantic candidate extraction + in-session model judgment against closed criteria
#   (synonym-renaming passages / inter-paragraph cohesion / colon sentences / triple isomorphic groups;
#    criteria in references/semantic-criteria.md; roughly 40-80 items per article)
python3 scripts/detect.py <file> --candidates --out /tmp/candidates.json

# Step 2: the model reviews hits and reports this article's measures, research significance,
#   examples, suggested edits and exclusions; then waits for the user's reply

# Step 3: after the reply, rewrite according to the accepted or adjusted plan (rules in SKILL.md)

# Step 4: recheck + before/after report (Markdown by default; --format html for a web version)
python3 scripts/detect.py <revised file> --json > /tmp/after.json
python3 scripts/report.py <original> <revised> /tmp/before.json /tmp/after.json \
    --semantic /tmp/candidates_labeled.json --out less-ai-tone-report.md
```

Detection runs in three layers: **script** (what can be counted from symbols; `detect.py`), **semantic** (four items that require understanding sentence meaning; the in-session model judges each against closed criteria), and **human review** (metaphor aptness, implicit metaphors, personifying metaphors; model agreement is only 0–40%, so these are listed but not judged).

Detection grades:

| Grade | Meaning | Handling |
|---|---|---|
| A | Mechanical fix: remove cue phrases, swap punctuation; zero semantic risk | Model reviews false positives and proposes edits; applied after the reply |
| B | Suggested fix: enumeration commas, long pre-modifiers; needs sentence restructuring | Model selects items one by one and proposes edits; applied after the reply |
| C | Report only: uniform sentence length, fragmented sections (whole-piece issues) | Not edited by default; handled only when the user asks |
| H | Human-review zone: metaphor aptness, personifying metaphors; the model cannot judge reliably | Kept by default; listed only when the user asks |
| X | Rejected: reverses in the matched retest, so not AI tone | Never edited; counts are shown to prevent accidental edits |
| F | Fingerprint: model-specific traits such as em dashes, semicolons, quotation marks | Reported with direction; safe local hits default to suggested edits; keeping one requires a specific reason |

### Preventing over-editing

The most common failure of model rewriting is overdoing it: to sound human, the model makes sentences erratically long or short, splits paragraphs and deletes normal expressions. SKILL.md sets six rewrite principles: **minimal change** (change only what each hit requires); **information conservation** (after rewriting, every content word must trace back to the original); **no manufactured irregularity** (sentence-length dispersion does not differ between human and machine, so do not change sentence length for rhythm); **keep the structure**; **follow the style reference** when one is supplied; and **three post-rewrite checks plus a retest**.

The structure section of the detection report (sentence-length CV, section-length CV, isomorphism per 100 paragraphs, heading density) labels which round and method each reference value comes from. The matched-retest human reference for sentence-length CV is 0.54. The round-one value of 0.67 is not mixed in, and no metric is pushed toward a target value. Mechanically adding irregularity is worse than not editing.

## 5 Methodological lessons

The study's own errors are recorded in [RESEARCH.md](./RESEARCH.md): six measurement errors (over-broad regexes, wrong denominators) and two results overturned by matched-pair retests.

## 6 Recomputation

```bash
# Single file or directory detection report
python3 scripts/detect.py <directory>

# Rule hit-rate comparison, human vs. generated corpus (bring your own corpus)
python3 scripts/compare-human-ai.py --human <dirs...> --ai <dirs...>

# Paragraph level: sentence isomorphism
# (zero-anaphora paragraph openings were removed on 2026-10-26: a weak signal, in the same family as the reversed "unclear reference" rule)
python3 scripts/check-structure.py --human <dirs...> --ai <dirs...>

# Translationese frequencies (generated side)
python3 scripts/check-translationese.py <dirs...>
```

The corpus is not redistributed because of copyright and privacy constraints. The scripts, definitions, and decision criteria are provided so the method can be rerun on a corpus you are allowed to use. The reported figures are observations from these samples, not a universal authorship detector.

## 7 Limitations

1. The semantic layer is single-model judgment. Spot checks show a 15–30% error rate: the direction is credible, exact percentages are not.
2. The human corpus varies widely between groups (em dash differences span about 100-fold). Expanding it may change some conclusions.
3. Models keep converging toward human writing. All frequencies are observations at one point in time.
4. Machines cannot measure metaphor aptness, whether examples are padded, or the quality of sentence variation. These need human reading.

**Rule set** [SKILL.md](./SKILL.md) · **Detection protocol** [DETECT.md](./DETECT.md) · **Full measurement record** [RESEARCH.md](./RESEARCH.md)

## 8 Installation and use

Ask an AI assistant that supports Agent Skills to install **Lieflat Less AI Tone** from this repository, or run:

```bash
npx skills add larashero3-dotcom/lieflat-less-ai-tone
```

Then give the assistant a finished Chinese article. It runs the scripts and assesses semantic candidates first, then reports findings with research benchmarks, original passages and concrete edits. Reply 「按建议改」 ("apply the suggestions") or narrow the scope; only then does it rewrite, recheck and produce a before-and-after comparison. Full demo: [Agent memory case](./examples/agent-memory-case/README.md).

---

**Data and code** [scripts/](./scripts/)

**License** [CC BY-NC 4.0](./LICENSE) (Attribution-NonCommercial 4.0; contact the author for commercial licensing)
