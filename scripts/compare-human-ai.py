#!/usr/bin/env python3
"""Compare a human corpus with an AI corpus on every detect.py metric, to (re)calibrate thresholds.

Usage:
    python3 scripts/compare-human-ai.py --human <dir> [more] --ai <dir> [more]

Each --human directory is measured separately as a group for a stability check; group values are never
printed (directory names and per-group numbers can expose corpus sources). Ratio = AI / human.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from detect import load_docs, measure_docs  # noqa: E402


def flat(r):
    return {**r["density"], **r["char_density"], **{k: v for k, v in r["structure"].items() if v is not None}}


def verdict(ratio):
    if ratio > 2:
        return "AI clearly more → candidate rule"
    if ratio > 1.25:
        return "AI slightly more"
    if ratio >= 0.8:
        return "no difference → should not be a rule"
    return "humans more → do not delete"


def main():
    human, ai, cur = [], [], None
    for a in sys.argv[1:]:
        cur = human if a == "--human" else ai if a == "--ai" else cur
        if a not in ("--human", "--ai") and cur is not None:
            cur.append(a)
    if not human or not ai:
        sys.exit(__doc__)

    groups = [flat(measure_docs(d)) for d in (load_docs(Path(h)) for h in human) if d]
    hd = [doc for h in human for doc in load_docs(Path(h))]
    ad = [doc for a in ai for doc in load_docs(Path(a))]
    if not groups or not ad:
        sys.exit(f"Empty corpus: human={len(hd)} docs, ai={len(ad)} docs")
    hr, ar = measure_docs(hd), measure_docs(ad)
    hm, am = flat(hr), flat(ar)

    print(f"Human: {len(hd)} docs, {hr['meta']['words']} words / AI: {len(ad)} docs, {ar['meta']['words']} words\n")
    head = f"{'Metric':<40}{'Human':>9}{'AI':>9}{'AI/H':>7}{'Stability':>11}  Verdict"
    print(head + "\n" + "-" * (len(head) + 30))
    for k in hm:
        h, a = hm[k], am.get(k, 0)
        ratio = a / h if h > 0.001 else float("inf")
        vals = [g.get(k, 0) for g in groups]
        stable = "stable" if max(vals) / max(min(vals), 0.01) <= 5 else "unstable"
        print(f"{k:<40}{h:>9.2f}{a:>9.2f}{ratio:>7.2f}{stable:>11}  {verdict(ratio)}")


if __name__ == "__main__":
    main()
