"""Paragraph-level structure comparison: same-structure adjacent sentences, zero-subject paragraph-opening comments.

Usage:
    python3 scripts/check-structure.py --human <dir...> --ai <dir...>

Why a separate script: both metrics use paragraphs as the denominator, not characters.
"Per 1k chars" is skewed by structural differences: AI averages 10 subheadings per doc and humans 1-2,
so per-char counts of question subheadings are inflated 30×; as a share of subheadings the gap disappears.
For metrics on structural elements, the denominator must be the total of the same kind of element.
"""
import re
import sys
from pathlib import Path

# Paragraph-opening comment phrases: without the anaphor, readers must look back at the previous paragraph
COMMENT = re.compile(
    r"^(?:听起来|看起来|看上去|听上去|说白了|说到底|换句话说|意味着|值得注意|"
    r"不难看出|细看|再看|回过头看|问题在于|原因在于|结果是|有意思的是|"
    r"更重要的是|关键在于|真正的)"
)
# Anaphors: link back to the preceding text
ANAPHOR = re.compile(r"^(?:这|那|其|此|上面|前面|刚才|以上|该|它|他|她|它们|他们|同样|类似|相比|反过来|但|不过|所以|因此|于是|而|另|除此|与此)")
# Metaphor openers (control item; humans use more)
METAPHOR = re.compile(r"^(?:像|就像|好比|好像|仿佛|如同|这就像)")


def paragraphs(text):
    out = []
    for p in text.split("\n"):
        p = p.strip()
        if len(p) < 8 or p.startswith(("#", "|", "```", ">", "- ", "* ", "!", "[")):
            continue
        out.append(p)
    return out


def signature(sent):
    """Sentence-structure signature: comma count, colon present, bracket present, length bucket."""
    return (sent.count("，"), "：" in sent, ("（" in sent or "(" in sent), len(sent) // 15)


def isomorphic(para, n):
    """Whether a paragraph has n consecutive sentences with the same signature."""
    sents = [s.strip() for s in re.split(r"[。！？]", para) if len(s.strip()) > 10]
    hits = 0
    for i in range(len(sents) - n + 1):
        sigs = [signature(s) for s in sents[i:i + n]]
        if all(s == sigs[0] for s in sigs) and sigs[0][0] >= 1:
            hits += 1
    return hits


def measure(texts):
    total = iso2 = iso3 = zero = meta = nonfirst = 0
    for t in texts:
        ps = paragraphs(t)
        total += len(ps)
        for i, p in enumerate(ps):
            iso2 += isomorphic(p, 2)
            iso3 += isomorphic(p, 3)
            if METAPHOR.match(p):
                meta += 1
            if i == 0:
                continue
            nonfirst += 1
            if COMMENT.match(p) and not ANAPHOR.match(p):
                zero += 1
    return {
        "paragraphs": total,
        "Isomorphic pairs per 100 paras": iso2 / total * 100 if total else 0,
        "Isomorphic triples per 100 paras": iso3 / total * 100 if total else 0,
        "Zero-subject comment opener %": zero / nonfirst * 100 if nonfirst else 0,
        "Metaphor opener/100 paras (ctrl)": meta / total * 100 if total else 0,
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


def main():
    human, ai, cur = [], [], None
    for a in sys.argv[1:]:
        if a == "--human":
            cur = human
        elif a == "--ai":
            cur = ai
        elif cur is not None:
            cur.append(a)
    if not human or not ai:
        print(__doc__)
        return

    groups = []
    for d in human:
        ts = load([d])
        if ts:
            groups.append((f"g{len(groups) + 1}", measure(ts)))
    hm = measure([t for d in human for t in load([d])])
    am = measure(load(ai))

    keys = [k for k in am if k != "paragraphs"]
    print(f"AI {am['paragraphs']} paragraphs, human {hm['paragraphs']} paragraphs\n")
    head = f"{'Metric':<34}{'AI':>8}{'Human':>8}{'Ratio':>7}{'Stability':>10}"
    print(head)
    print("-" * len(head))
    for k in keys:
        a, h = am[k], hm[k]
        r = a / h if h > 0.001 else float("inf")
        # Per-group values are used only for stability, not printed
        vals = [m[k] for _, m in groups]
        spread = max(vals) / max(min(vals), 0.01)
        print(f"{k:<34}{a:>8.2f}{h:>8.2f}{r:>6.2f}×{'stable' if spread <= 5 else 'unstable':>10}")


if __name__ == "__main__":
    main()
