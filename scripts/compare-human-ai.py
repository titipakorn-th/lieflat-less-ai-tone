"""Rule-hit-rate comparison: human corpus vs AI corpus.

Usage:
    python3 scripts/compare-human-ai.py --human <dir> [more] --ai <dir> [more]

Why this script: the "discrimination ×N" figures in SKILL.md all come from old measurements that are no
longer usable, and its sentence splitting was flawed. This script measures the human and AI sides the same
way, so each rule's ratio is reproducible. Ratio = human frequency / AI frequency (<1 means AI uses it more).
"""
import re
import sys
import collections
from pathlib import Path

# Each entry maps to one SKILL.md rule; regexes follow the rule's trigger markers as closely as possible
RULES = {
    "2 Contrast reversal": r"(?:不是|并非|不在于)[^，。！？\n]{1,20}[，]?(?:而是|而在于)",
    # The original regex banned spaces and Latin letters, so it missed lists like 「用哪个模型、Team Skill 开关、定时任务」
    "3 Dense enumeration commas": r"[^，。！？；：、\n]{1,14}、[^，。！？；：、\n]{1,14}、[^，。！？；：、\n]{1,14}",
    # Intra-sentence parallel isomorphism removed from the rules: humans use it no less than AI; measurement kept for re-checks
    "(removed) intra-sentence isomorphism: 更X": r"更[一-鿿]{1,3}[、，][^，。\n]{0,8}更[一-鿿]{1,3}",
    "(removed) intra-sentence isomorphism: same-char pair": r"([一-鿿]{1,2})[^，。、\n]{2,12}[、，]\1[^，。、\n]{2,12}",
    # Question rules were removed from SKILL.md and are no longer counted. Three rounds of measurement were unstable:
    #   question-mark total: humans appear 2.5× higher, but driven by a few groups; inconsistent across groups
    #   self-posed questions: ratio 1.03; a wide regex also catches new sentences like 「？这是另一个问题」
    #   question subheadings: 32× per 1k chars; as a share of subheadings AI 2.7% / human max 3.6%; no difference
    # Lesson: for metrics on structural elements, first confirm the denominators are comparable.
    "4 Em dash": r"——",
    # Matches only cue phrase + colon (introducing a summary/conclusion/cause/definition); not dialogue, headings, lists, or ordinary colons
    "5 Cue-phrase colon": (r"(?:一句话(?:总结|说|概括)|简单说|说白了|总结|小结|结论|核心(?:是|在于|观点)?"
                    r"|关键(?:是|在于)?|重点(?:是)?|原因(?:如下|有|在于)?|问题(?:是|在于)?"
                    r"|答案(?:是)?|本质(?:是|上)?|定义(?:是)?|具体(?:来说|如下|包括)?"
                    r"|举例(?:来说)?|换句话说|也就是说|我的(?:观点|判断|结论)|建议(?:是)?)[：:]"),
    "6 Ordinal as subheading": r"(?:^|\n)\s*(?:首先|其次|再次|最后|第一|第二|第三|一方面|另一方面)[，、]",
    "(removed) 就 char": r"就",
    "(removed) 很 char": r"很",
    "(removed) 了 char": r"了",
    "(removed) colloquial connectives": r"但是|其实|不过|就是",
    "9 Verb nominalization": r"(?:完成|实现|进行|开展)了?(?:对)?[^，。\n]{0,10}的(?:优化|提升|调整|分析|改造|升级)",
    "11 Long pre-modifier": r"(?:一个|一种|一套|这种|这个)[^，。、；：！？\n]{15,}的[一-鿿]{2,5}",
    "11 当…时 clause": r"当[^，。\n]{2,20}(?<!的时候)时，",
    "11 Topic-shell frame": r"(?:对于[^，。\n]{2,15}来说|对[^，。\n]{2,15}而言|就[^，。\n]{2,15}而言|在[^，。\n]{2,12}方面)",
    "11 Sentence-initial connective": r"(?:^|\n)\s*(?:然而|因此|此外|与此同时|换言之|总而言之)[，、]",
    '11 "This means" restatement': r"(?:这意味着|这表明|这说明|换句话说)",
}


def load(dirs):
    out = []
    for d in dirs:
        for f in Path(d).rglob("*.md"):
            if f.parent.name == "_meta":
                continue
            try:
                out.append(f.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, OSError):
                continue
    return out


def measure(texts):
    joined = "\n".join(texts)
    k = len(re.findall(r"[一-鿿]", joined)) / 1000
    hits = {}
    for name, pat in RULES.items():
        rx = re.compile(pat)
        n = len(rx.findall(joined))
        docs = sum(1 for t in texts if rx.search(t))
        hits[name] = (n / k if k else 0, n, docs)
    return hits, k, len(texts)


def parse_args(argv):
    human, ai, cur = [], [], None
    for a in argv:
        if a == "--human":
            cur = human
        elif a == "--ai":
            cur = ai
        elif cur is not None:
            cur.append(a)
    return human, ai


def main():
    hd, ad = parse_args(sys.argv[1:])
    if not hd or not ad:
        print(__doc__)
        return

    # Measure each human directory separately to check whether differences are stable within the corpus (no per-group output)
    per_author = {}
    for d in hd:
        texts = load([d])
        if texts:
            # Neither directory names as labels nor per-group values are printed: corpus directory names often carry
            # source info, and listing groups exposes the corpus composition. Used only for the stability check.
            per_author[f"g{len(per_author) + 1}"] = measure(texts)
    ha = load(ad)
    if not per_author or not ha:
        print(f"Empty corpus: human={len(per_author)} groups, ai={len(ha)} docs")
        return

    all_human = [t for d in hd for t in load([d])]
    hh, hk, hn = measure(all_human)
    ah, ak, an = measure(ha)

    names = list(per_author)
    print(f"Human corpus: {hn} docs, {hk/10:.1f} 10k Han chars")
    print(f"AI corpus: {an} docs, {ak/10:.1f} 10k Han chars\n")

    head = f"{'Rule':<30}{'Human':>8}{'AI':>7}{'Ratio':>8}{'Stability':>10}  Verdict"
    print(head)
    print("-" * (len(head) + 6))

    rows = []
    for name in RULES:
        h, a = hh[name][0], ah[name][0]
        ratio = h / a if a > 0.001 else float("inf")
        rows.append((ratio, name, h, a))

    for ratio, name, h, a in sorted(rows, key=lambda r: r[0]):
        disp = f"{ratio:>7.2f}" if ratio != float("inf") else "      ∞"
        # Per-group values are used only for stability, not printed (listing them exposes the corpus composition)
        vals = [per_author[n][0][name][0] for n in names]
        spread = max(vals) / max(min(vals), 0.01)
        stable = "stable" if spread <= 5 else "unstable"
        if ratio < 0.5:
            verdict = "AI clearly more → worth fixing"
        elif ratio < 0.8:
            verdict = "AI slightly more"
        elif ratio <= 1.25:
            verdict = "no difference → should not be a rule"
        elif ratio <= 3:
            verdict = "humans more"
        else:
            verdict = "humans clearly more → direction is to add"
        if spread > 5 and ratio > 1.25:
            verdict += " (large within-corpus variation; possibly genre)"
        print(f"{name:<30}{h:>8.2f}{a:>7.2f}{disp}{stable:>10}  {verdict}")


if __name__ == "__main__":
    main()
