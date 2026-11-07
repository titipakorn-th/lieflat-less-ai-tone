# Lieflat Less AI Tone

![Lieflat Less AI Tone: 5.2M characters, 100+ measures, approximately 500K model semantic judgments](assets/less-ai-tone-hero-en.png)

**A post-draft "less AI tone" skill for English prose.** It reports what it finds, with research benchmarks, cited passages from your draft, and proposed edits. It rewrites and rechecks only after you reply.

The rule set derives from a two-round study of Chinese corpora: 1,169 articles, about 5.2 million Chinese characters, 100+ measures, and about 500,000 model semantic judgments. The English port keeps the study's rule directions and drops the Chinese-only rules (the "when…" temporal clause and long pre-modifier rules). The study's thresholds are not calibrated for English. To recalibrate, run `scripts/compare-human-ai.py` on a human English corpus and an AI English corpus you are allowed to use, then update the reference constants in `scripts/detect.py`.

## Why it exists

Strong models often produce long drafts that read as machine-written, and the usual fixes have limits:

- **Word lists miss the signal.** Many texts avoid buzzwords such as "empower", "closed loop" and "handle", yet still read as AI-written after three paragraphs.
- **Bulk rules cause over-editing.** Given a dozen rules, a model deletes natural rhetorical questions and numbered headings, and splits fluent sentences to satisfy "vary sentence length."

This project measures the habits that objectively reflect model writing, quantifies them, and only then writes rules. Two principles guide it: each measure maps to one locatable problem (validity), and every before/after change is quantified (reliability).

## Rules

| Grade | Rule | Example pattern | Handling |
|---|---|---|---|
| A | Contrast reversal | "It is not a technical problem but a cognitive one." | State the claim directly |
| A | Cue-phrase colon | "The core issue is: cost." | Drop the cue, write the content |
| A | Opening formula | "To put it bluntly, ..." | Delete; state the judgment |
| A | Topic-shell frame | "When it comes to memory, ..." | Make the topic the subject |
| A | Sentence-initial connective | "However, ..." | Move it, use a plainer word, or drop it |
| B | Serial list (3 or more items) | "speed, cost, and reliability" | Summarize, or change the syntax of one item |
| B | Synonym rotation | "improve / enhance / boost" in one paragraph | Review each hit |
| C | Structure and rhythm | Uniform sentence or section lengths | Report only |
| F | Fingerprints | Em dashes, semicolons, quotation marks | Reported with direction; model-specific |
| H | Personifying metaphor | "Think of it as a diligent assistant." | Asked for only; metaphor aptness needs a human |
| X | Rejected | Vague summaries, numbered subheadings, "This means" restatements, empty lead-ins to lists | Counted, never edited |

Grades A and B are edited after your reply. Grades C, F and H are reported. Grade X exists to prevent over-editing: in the matched retest these features were equal between models and humans or reversed, so they are not AI tone.

## Study basis

- **Round one:** 629 articles. 300 AI articles (five models, 60 each) against 329 human articles, same topic range.
- **Round two:** 270 matched pairs. Each pair shares topic, facts and length. GPT-5.6 wrote 135 and Claude Opus 4.6 wrote 135, analyzed separately.
- **Layers:** script (90 countable measures, paired Wilcoxon and Cliff's δ), semantic (structured model judgments against closed criteria), and human review (metaphor aptness).

Full methods, tables and corrections are in [RESEARCH.md](./RESEARCH.md).

## Workflow

```bash
# Step 1: script detection (report only; --json saves results for step 4)
python3 scripts/detect.py <file or directory> --json > /tmp/before.json

# Step 1.5: semantic candidates, judged by the in-session model against references/semantic-criteria.md
python3 scripts/detect.py <file> --candidates --out /tmp/candidates.json

# Step 2: the model reviews hits and reports findings, examples and proposed edits, then waits for your reply
# Step 3: after your reply, rewrite the accepted plan (rules in SKILL.md)

# Step 4: recheck and produce a before/after report (Markdown by default; --format html for a web version)
python3 scripts/detect.py <revised file> --json > /tmp/after.json
python3 scripts/report.py <original> <revised> /tmp/before.json /tmp/after.json \
    --semantic /tmp/candidates_labeled.json --out less-ai-tone-report.md
```

Detection has three layers: **script** (what can be counted from symbols; `detect.py`), **semantic** (four candidate types that need sentence-meaning judgment), and **human review** (metaphor aptness and personifying metaphors, which models judge unreliably).

## Recomputation

```bash
# Detection report for a file or directory
python3 scripts/detect.py <directory>

# Human vs. AI corpus comparison on every detect.py metric (bring your own corpus)
python3 scripts/compare-human-ai.py --human <dirs...> --ai <dirs...>

# Smoke test for detection patterns
python3 scripts/test_detect.py
```

The corpus is not redistributed because of copyright and privacy constraints. The scripts, definitions and criteria are provided so the method can be rerun on a corpus you are allowed to use. Reported figures are observations from the study's samples, not a universal authorship detector.

## Limitations

1. The semantic layer is single-model judgment. Spot checks show a 15–30% error rate: the direction is credible, exact percentages are not.
2. The human corpus varies widely between groups (em dash rates differ about 100-fold). Expanding it may change some conclusions.
3. Models keep converging toward human writing, so all frequencies are observations at one point in time.
4. Machines cannot judge metaphor aptness, padded examples, or the quality of sentence variation. These need human reading.

## Example case

[Agent memory case](./examples/agent-memory-case/README.md) runs one English article through every stage: original, detection and suggestions, revision, side-by-side HTML comparison, and retest. Data files hold the before and after script results and the per-item semantic labels.

## Installation and use

Ask an AI assistant that supports Agent Skills to install **Lieflat Less AI Tone** from this repository, or run:

```bash
npx skills add larashero3-dotcom/lieflat-less-ai-tone
```

Then give the assistant a finished English article. It runs the scripts and assesses semantic candidates first, then reports findings with research benchmarks, original passages and concrete edits. Reply "apply the suggestions" or narrow the scope; only then does it rewrite, recheck and produce a before-and-after comparison.

---

**Data and code** [scripts/](./scripts/) · **Rule set** [SKILL.md](./SKILL.md) · **Detection protocol** [DETECT.md](./DETECT.md)

**License** [CC BY-NC 4.0](./LICENSE) (Attribution-NonCommercial 4.0; contact the author for commercial licensing)
