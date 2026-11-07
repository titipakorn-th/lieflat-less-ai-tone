#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Less AI tone v2 · before/after report: metric comparison + graded findings + marked before/after diff.

Default output is Markdown (same format as the draft, markdown markers kept, copyable back into the
writing workflow). `--format html` produces a single-file web page.

Usage (run detect.py --json before and after the edit, then generate the report):
    python3 scripts/detect.py before.md --json > /tmp/before.json
    python3 scripts/detect.py after.md --json > /tmp/after.json
    python3 scripts/report.py before.md after.md /tmp/before.json /tmp/after.json \
        [--semantic judgments.json] [--out report.md] [--format md|html]

--semantic (optional): JSON of candidates from detect.py --candidates, judged by Claude per
references/semantic-criteria.md (entries carry label/confidence/reason fields).

Standard library only; no external dependencies.
Markdown diff convention: <del> = original text removed/replaced; <ins> = new revised text.
"""
import argparse
import difflib
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from detect import REGEX_HITS  # name → grade mapping (A/B/H/X)

# ---------------- Metric display config ----------------

# Top metric table: key → (display name, better direction, reference)
# References: human medians from the 270 matched pairs in RESEARCH.md (Chinese corpus; direction only).
METRIC_ROWS = [
    ("Contrast reversal", "'Not A but B' contrast", "low", 0.22),
    ("Cue-phrase colon", "Conclusion-cue colon", "low", 0.08),
    ("Serial list ≥3", "Dense lists", "low", 1.78),
]

STRUCT_ROWS = [
    ("Sentence-length CV", "Sentence-length variation", "higher = more varied", "human ≈0.54 / AI ≈0.46"),
    ("Section-length CV", "Section-length variation", "higher = more varied", "human ≈0.83 / AI ≈0.31"),
    ("Headings per 1k words", "Section density", "lower = whole piece written continuously", "human ≈0.32 / AI ≈1.26"),
    ("Isomorphic pairs per 100 paras", "Adjacent-sentence isomorphism", "lower is better", "human ≈5.52 / AI ≈8.71"),
    ("Isomorphic triples per 100 paras", "Triple isomorphism (coarse)", "lower is better", "human ≈0.41 / AI ≈0.84"),
    ("MTLD (rough)", "Lexical variety", "below human ≈ natural", "human ≈143 / AI ≈227"),
]

FINGERPRINT_ROWS = [
    ("Em dash", "Opus heavy +0.95 / GPT light −0.54; opposite directions, read per model"),
    ("Semicolon", "GPT fingerprint δ+0.80; Opus no difference"),
    ("Quotation marks", "Opus uses fewer δ−0.67; report only, do not edit"),
]

CSS = """
body{font-family:-apple-system,sans-serif;max-width:760px;margin:40px auto;line-height:1.9;font-size:16px;padding:0 20px;color:#222}
h1{font-size:22px}h2{font-size:19px;border-bottom:2px solid #ccc;padding-bottom:6px;margin-top:2.2em}
h3{font-size:16px;margin-bottom:0.4em}
table{border-collapse:collapse;width:100%;font-size:14px;margin:0.6em 0 1.4em}
th,td{border:1px solid #ddd;padding:5px 10px;text-align:left;vertical-align:top}
th{background:#f5f5f5}
.warn{background:#fff3cd;padding:14px 18px;border-radius:8px;margin-bottom:1.5em;font-size:14px}
.legend{color:#555;margin-bottom:2em;font-size:14px}
.chg,.ins{color:#d32f2f;font-weight:600}
.del{color:#aaa;text-decoration:line-through}
.up{color:#c62828;font-weight:600}.down{color:#2e7d32;font-weight:600}.flat{color:#777}
.tagA{background:#e3f2fd;padding:1px 7px;border-radius:4px;font-size:12px}
.tagB{background:#fff3e0;padding:1px 7px;border-radius:4px;font-size:12px}
.tagC{background:#f3e5f5;padding:1px;border-radius:4px;font-size:12px}
.tagF{background:#eceff1;padding:1px 7px;border-radius:4px;font-size:12px}
.tagX{background:#fafafa;color:#888;padding:1px 7px;border-radius:4px;font-size:12px}
.tagH{background:#fce4ec;padding:1px 7px;border-radius:4px;font-size:12px}
.small{color:#777;font-size:13px}
.human{color:#2e7d32}
details{margin:0.3em 0}
summary{cursor:pointer}
p{margin:0 0 1.1em}
"""


def esc(s):
    return html.escape(str(s), quote=False)


def arrow(before, after, better="low"):
    """better: 'low' = lower is better, 'high' = higher is better, None = no direction"""
    if before is None or after is None or before == after:
        cls, mark = "flat", "→"
    elif better == "low":
        cls, mark = ("down", "↓") if after < before else ("up", "↑")
    elif better == "high":
        cls, mark = ("up", "↑") if after > before else ("down", "↓")
    else:
        cls, mark = "flat", "→"
    return f'<span class="{cls}">{mark}</span>'


# ---------------- Metric comparison table ----------------

def metric_table(d0, d1):
    rows = []
    for key, name, better, ref in METRIC_ROWS:
        v0 = d0["density"].get(key)
        v1 = d1["density"].get(key)
        rows.append(f"<tr><td>{esc(name)}</td>"
                    f"<td>{v0 if v0 is not None else '—'}</td>"
                    f"<td>{v1 if v1 is not None else '—'}</td>"
                    f"<td>{arrow(v0, v1, better)}</td>"
                    f'<td class="human">≈{ref}</td></tr>')
    for key, name, better, ref in STRUCT_ROWS:
        v0 = d0["structure"].get(key)
        v1 = d1["structure"].get(key)
        rows.append(f"<tr><td>{esc(name)}</td>"
                    f"<td>{v0 if v0 is not None else '—'}</td>"
                    f"<td>{v1 if v1 is not None else '—'}</td>"
                    f"<td>{arrow(v0, v1, better)}</td>"
                    f'<td class="human">{esc(ref)}</td></tr>')
    for key, note in FINGERPRINT_ROWS:
        v0 = d0["char_density"].get(key)
        v1 = d1["char_density"].get(key)
        rows.append(f"<tr><td>{esc(key)}<span class='small'> (fingerprint)</span></td>"
                    f"<td>{v0}</td><td>{v1}</td><td>{arrow(v0, v1, None)}</td>"
                    f'<td class="small">{esc(note)}</td></tr>')
    return ("<table><tr><th>Metric</th><th>Before</th><th>After</th><th>Change</th>"
            "<th>Human ref</th></tr>" + "".join(rows) + "</table>"
            '<p class="small">↓/↑ green = moved toward the human reference (improved), red = worse; fingerprint rows have no direction. '
            "Reference values = human medians from 270 matched pairs (per 1k words or CV; Chinese-corpus study, direction only); see RESEARCH.md.</p>")


# ---------------- Graded findings ----------------

def findings_section(d):
    out = []
    for lvl, title, cls in [("A", "Mechanical fixes (after model review removes false positives)", "tagA"),
                            ("B", "Suggested fixes (model filters item by item)", "tagB"),
                            ("H", "Human-review zone (kept by default; review only if the user asks)", "tagH"),
                            ("X", "Rejected features (measured as not AI tone; do not edit)", "tagX")]:
        names = [nm for lv, nm, *_ in REGEX_HITS if lv == lvl]
        rows = []
        for nm in names:
            hs = d["hits"].get(nm, [])
            if not hs:
                continue
            rows.append(f"<div><strong>{esc(nm)}</strong> {len(hs)} hits")
            rows.append("<details><summary class='small'>show hits</summary>")
            for h in hs[:20]:
                rows.append(f"<p class='small'>{esc(h['file'])}:{h['line']}  "
                            f"{esc(h['excerpt'])}</p>")
            rows.append("</details></div>")
        if rows:
            out.append(f'<h3><span class="{cls}">{lvl}</span> {esc(title)}</h3>')
            out.extend(rows)
    return "\n".join(out)


def semantic_section(sem):
    """Semantic-layer judgments: per-item summary + collapsed details."""
    if not sem:
        return ""
    out = ['<h2>Semantic-layer judgments (in-session model judges item by item per the experiment criteria)</h2>',
           '<p class="small">Four items are statistically significant in the 270-pair corpus; synonym renaming rests on a '
           'single-model criterion (one tier weaker). Criteria: references/semantic-criteria.md.</p>']
    groups = {"rename": "Synonym renaming (paragraph level)", "cohesion": "Cohesion method (inter-paragraph interface)",
              "colon": "Colon classification", "iso3": "Highly isomorphic triples"}
    for key, title in groups.items():
        items = [c for c in sem.get(key, []) if c.get("label")]
        if not items:
            continue
        counts = {}
        for c in items:
            counts[c["label"]] = counts.get(c["label"], 0) + 1
        stats = ", ".join(f"{esc(k)} {v}" for k, v in sorted(counts.items(), key=lambda x: -x[1]))
        out.append(f"<h3>{esc(title)} <span class='small'>{len(items)} items: {stats}</span></h3>")
        flagged = [c for c in items if c.get("label") in {
            "2 groups", "3+ groups",                 # heavy renaming
            "explicit carry-over",                   # cohesion chain (run length counted separately)
            "conclusion cue",                        # real colon signal
            "highly isomorphic",                     # real isomorphism signal
        }]
        # cohesion chain length
        chain_note = ""
        if key == "cohesion":
            labels = [c.get("label") for c in items]
            best = cur = 0
            for lb in labels:
                cur = cur + 1 if lb == "explicit carry-over" else 0
                best = max(best, cur)
            chain_note = f" (longest chain {best} interfaces; ≥6 is an AI feature, human median 2)"
            if best >= 6:
                chain_note = f'<span class="up">⚠ {chain_note}</span>'
        if key == "cohesion" and chain_note:
            out.append(f"<p>{chain_note}</p>")
        for c in flagged[:15]:
            text = c.get("para") or " → ".join(filter(None, [
                c.get("prev_tail"), c.get("next_head")])) or c.get("sentence") \
                or " / ".join(c.get("sents") or [])
            conf = c.get("confidence", "")
            reason = c.get("reason", "")
            out.append(f"<p class='small'><strong>{esc(c['label'])}</strong>"
                       f" (confidence: {esc(conf)}) {esc(c.get('file',''))}:{c.get('line','')}  "
                       f"{esc(text[:110])}"
                       + (f"<br>reason: {esc(reason[:100])}" if reason else "") + "</p>")
    return "\n".join(out)


# ---------------- Marked diff ----------------

def para_split(text):
    """Split on blank lines, keeping the original form (markdown markers kept)."""
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paras


def tokens(s):
    """Words and the whitespace between them, so diffs land on word boundaries."""
    return re.findall(r"\s+|\S+", s)


def inline_diff(a, b):
    """Word-level diff within a paragraph: same = black, deleted = grey strikethrough, changed/added = red."""
    a, b = tokens(a), tokens(b)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        x, y = "".join(a[i1:i2]), "".join(b[j1:j2])
        if tag == "equal":
            out.append(esc(x))
        elif tag == "delete":
            out.append(f'<span class="del">{esc(x)}</span>')
        elif tag == "insert":
            out.append(f'<span class="ins">{esc(y)}</span>')
        elif tag == "replace":
            out.append(f'<span class="del">{esc(x)}</span><span class="chg">{esc(y)}</span>')
    return "".join(out)


def diff_section(text0, text1):
    p0, p1 = para_split(text0), para_split(text1)
    sm = difflib.SequenceMatcher(None, p0, p1, autojunk=False)
    body = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for p in p0[i1:i2]:
                body.append(f"<p>{esc(p)}</p>")
        elif tag == "delete":
            for p in p0[i1:i2]:
                body.append(f'<p><span class="del">{esc(p)}</span></p>')
        elif tag == "insert":
            for p in p1[j1:j2]:
                body.append(f'<p><span class="ins">{esc(p)}</span></p>')
        elif tag == "replace":
            for pa, pb in zip(p0[i1:i2], p1[j1:j2]):
                body.append(f"<p>{inline_diff(pa, pb)}</p>")
            # mark extra paragraphs separately when counts differ
            for p in p0[i1 + (j2 - j1):i2]:
                body.append(f'<p><span class="del">{esc(p)}</span></p>')
            for p in p1[j1 + (i2 - i1):j2]:
                body.append(f'<p><span class="ins">{esc(p)}</span></p>')
    return "\n".join(body)


# ---------------- Markdown report ----------------

def arrow_md(before, after, better="low"):
    if before is None or after is None or before == after:
        return "→"
    if better == "low":
        return "↓" if after < before else "↑"
    if better == "high":
        return "↑" if after > before else "↓"
    return "→"


def metric_table_md(d0, d1):
    rows = ["| Metric | Before | After | Change | Human ref |", "|---|---|---|---|---|"]
    for key, name, better, ref in METRIC_ROWS:
        v0 = d0["density"].get(key)
        v1 = d1["density"].get(key)
        rows.append(f"| {name} | {v0 if v0 is not None else '—'} | "
                    f"{v1 if v1 is not None else '—'} | {arrow_md(v0, v1, better)} | ≈{ref} |")
    for key, name, better, ref in STRUCT_ROWS:
        v0 = d0["structure"].get(key)
        v1 = d1["structure"].get(key)
        rows.append(f"| {name} | {v0 if v0 is not None else '—'} | "
                    f"{v1 if v1 is not None else '—'} | {arrow_md(v0, v1, better)} | {ref} |")
    for key, note in FINGERPRINT_ROWS:
        v0 = d0["char_density"].get(key)
        v1 = d1["char_density"].get(key)
        rows.append(f"| {key} (fingerprint) | {v0} | {v1} | {arrow_md(v0, v1, None)} | {note} |")
    rows.append("")
    rows.append("↓/↑ = improved/worsened toward the human reference; fingerprint rows have no direction. "
                "Reference values = human medians from 270 matched pairs (per 1k words or CV; Chinese-corpus study, direction only); see RESEARCH.md.")
    return "\n".join(rows)


def findings_section_md(d):
    out = []
    for lvl, title in [("A", "Mechanical fixes (after model review removes false positives)"),
                       ("B", "Suggested fixes (model filters item by item)"),
                       ("H", "Human-review zone (kept by default; review only if the user asks)"),
                       ("X", "Rejected features (measured as not AI tone; do not edit)")]:
        names = [nm for lv, nm, *_ in REGEX_HITS if lv == lvl]
        blocks = []
        for nm in names:
            hs = d["hits"].get(nm, [])
            if not hs:
                continue
            lines = [f"**{nm}** {len(hs)} hits", ""]
            for h in hs[:20]:
                lines.append(f"- `{h['file']}:{h['line']}`  {h['excerpt']}")
            lines.append("")
            blocks.append("\n".join(lines))
        if blocks:
            out.append(f"### Grade {lvl} · {title}\n")
            out.extend(blocks)
    return "\n".join(out)


def semantic_section_md(sem):
    if not sem:
        return ""
    out = ["## Semantic-layer judgments (in-session model judges item by item per the experiment criteria)", "",
           "Four items are statistically significant in the 270-pair corpus; synonym renaming rests on a "
           "single-model criterion (one tier weaker). Criteria: references/semantic-criteria.md.", ""]
    groups = {"rename": "Synonym renaming (paragraph level)", "cohesion": "Cohesion method (inter-paragraph interface)",
              "colon": "Colon classification", "iso3": "Highly isomorphic triples"}
    for key, title in groups.items():
        items = [c for c in sem.get(key, []) if c.get("label")]
        if not items:
            continue
        counts = {}
        for c in items:
            counts[c["label"]] = counts.get(c["label"], 0) + 1
        stats = ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda x: -x[1]))
        out.append(f"### {title} ({len(items)} items: {stats})")
        out.append("")
        if key == "cohesion":
            labels = [c.get("label") for c in items]
            best = cur = 0
            for lb in labels:
                cur = cur + 1 if lb == "explicit carry-over" else 0
                best = max(best, cur)
            note = f"Longest chain {best} interfaces; ≥6 is an AI feature, human median 2."
            if best >= 6:
                note = f"⚠ {note}"
            out.append(note)
            out.append("")
        flagged = [c for c in items if c.get("label") in {
            "2 groups", "3+ groups", "explicit carry-over", "conclusion cue", "highly isomorphic",
        }]
        for c in flagged[:15]:
            text = c.get("para") or " → ".join(filter(None, [
                c.get("prev_tail"), c.get("next_head")])) or c.get("sentence") \
                or " / ".join(c.get("sents") or [])
            conf = c.get("confidence", "")
            reason = c.get("reason", "")
            out.append(f"- **{c['label']}** (confidence: {conf}) `{c.get('file','')}:{c.get('line','')}`  {text[:110]}"
                       + (f"  reason: {reason[:100]}" if reason else ""))
        out.append("")
    return "\n".join(out)


def inline_diff_md(a, b):
    """Markdown version of the within-paragraph word diff: <del> = original, <ins> = new text.

    Uses inline HTML tags rather than ~~ / **: edits often fall inside or beside existing **bold**,
    ## headings and other markdown markers, where ~~ / ** pair up wrongly (nesting breaks).
    <del>/<ins> are valid inline HTML and never clash with markdown markers; Typora, VS Code and
    GitHub previews render them correctly (strikethrough/underline).
    """
    a, b = tokens(a), tokens(b)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        x, y = "".join(a[i1:i2]), "".join(b[j1:j2])
        if tag == "equal":
            out.append(x)
        elif tag == "delete":
            out.append(f"<del>{x}</del>")
        elif tag == "insert":
            out.append(f"<ins>{y}</ins>")
        else:  # replace
            out.append(f"<del>{x}</del><ins>{y}</ins>")
    return "".join(out)


def diff_section_md(text0, text1):
    p0, p1 = para_split(text0), para_split(text1)
    sm = difflib.SequenceMatcher(None, p0, p1, autojunk=False)
    body = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            body.extend(p0[i1:i2])
        elif tag == "delete":
            body.extend(f"<del>{p}</del>" for p in p0[i1:i2])
        elif tag == "insert":
            body.extend(f"<ins>{p}</ins>" for p in p1[j1:j2])
        elif tag == "replace":
            for pa, pb in zip(p0[i1:i2], p1[j1:j2]):
                body.append(inline_diff_md(pa, pb))
            for p in p0[i1 + (j2 - j1):i2]:
                body.append(f"<del>{p}</del>")
            for p in p1[j1 + (i2 - i1):j2]:
                body.append(f"<ins>{p}</ins>")
    return "\n\n".join(body)


def build_report_md(t0, t1, d0, d1, sem, name0, name1):
    parts = [
        "# Less AI tone · before/after report",
        "",
        f"{name0} → {name1}",
        "",
        "Markup: <del>strikethrough</del> = original text removed/replaced; <ins>underline</ins> = new revised text; "
        "in the metric table, ↓/↑ = improved/worsened relative to the human reference.",
        "",
        "## 1. Metric comparison",
        "",
        metric_table_md(d0, d1),
    ]
    sem_md = semantic_section_md(sem)
    if sem_md:
        parts.append(sem_md)
    parts.extend([
        "## 2. Graded findings (before-edit detection)",
        "",
        findings_section_md(d0),
        "Grade C (structure/rhythm) is in the metric table; F (fingerprint) is in its fingerprint rows; "
        "metaphor fit can only be judged by human review, so it is kept this round. "
        "Relevant sentences are listed for judgment only when the user asks.",
        "",
        "## 3. Side-by-side (full revised text, changes marked)",
        "",
        diff_section_md(t0, t1),
    ])
    return "\n\n".join(parts)


# ---------------- Assembly ----------------

def build_report(t0, t1, d0, d1, sem, name0, name1):
    parts = [
        "<!DOCTYPE html><html><head><meta charset=\"utf-8\">",
        f"<title>Less-AI-tone report · {esc(name0)}</title><style>{CSS}</style></head><body>",
        f"<h1>Less AI tone · before/after report</h1>",
        f'<p class="small">{esc(name0)} → {esc(name1)}</p>',
        '<div class="legend">Legend: <span class="chg">red</span> = new revised text; '
        '<span class="del">grey strikethrough</span> = original text removed/replaced; '
        'in the metric table, ↓/↑ = improved/worsened relative to the human reference.</div>',
        "<h2>1. Metric comparison</h2>",
        metric_table(d0, d1),
        semantic_section(sem),
        "<h2>2. Graded findings (before-edit detection)</h2>",
        findings_section(d0),
        '<p class="small">Grade C (structure/rhythm) is in the metric table; F (fingerprint) is in its fingerprint rows; '
        "metaphor fit can only be judged by human review, so it is kept this round. "
        "Relevant sentences are listed for judgment only when the user asks.</p>",
        "<h2>3. Marked before/after comparison</h2>",
        diff_section(t0, t1),
        "</body></html>",
    ]
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before", help="before text file")
    ap.add_argument("after", help="after text file")
    ap.add_argument("json_before", help="before detect --json output")
    ap.add_argument("json_after", help="after detect --json output")
    ap.add_argument("--semantic", help="semantic judgment JSON (candidates + label fields)")
    ap.add_argument("--format", choices=["md", "html"], default="md",
                    help="report format: md = Markdown (default; same format as the draft, copyable), html = single-file web page")
    ap.add_argument("--out", default=None,
                    help="output path; default name less-ai-tone-report.md / .html")
    args = ap.parse_args()

    t0 = Path(args.before).read_text(encoding="utf-8", errors="ignore")
    t1 = Path(args.after).read_text(encoding="utf-8", errors="ignore")
    d0 = json.loads(Path(args.json_before).read_text(encoding="utf-8"))
    d1 = json.loads(Path(args.json_after).read_text(encoding="utf-8"))
    sem = None
    if args.semantic:
        sem = json.loads(Path(args.semantic).read_text(encoding="utf-8"))

    out = args.out or f"less-ai-tone-report.{args.format}"
    if args.format == "md":
        page = build_report_md(t0, t1, d0, d1, sem, args.before, args.after)
    else:
        page = build_report(t0, t1, d0, d1, sem, args.before, args.after)
    Path(out).write_text(page, encoding="utf-8")
    w0, w1 = len(t0.split()), len(t1.split())
    print(f"Report → {out} (before {w0} words / after {w1} words, change {w1 - w0:+d})")


if __name__ == "__main__":
    main()
