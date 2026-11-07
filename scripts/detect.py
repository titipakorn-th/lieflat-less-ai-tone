#!/usr/bin/env python3
"""Less AI tone, step 1: detect only, never rewrite. Analyzes English prose (.md/.txt).

Usage:
    python3 scripts/detect.py <file-or-dir> [--json] [--max-hits 5]
    python3 scripts/detect.py <file> --candidates [--out candidates.json]

--candidates extracts semantic-layer candidates (rename / cohesion / colon / iso3) for the in-session
model to judge per references/semantic-criteria.md.

Grades:
    A mechanical fix   fixed phrasing/punctuation; model reviews, user approves, then edit
    B suggested fix    needs restructuring; model reviews each hit, user approves, then edit
    C report only      structure/rhythm distributions; not edited by default
    F fingerprint      per-model habits (em dash / semicolon / quotes); always read with direction
    H human review     metaphor aptness; listed only when the user asks
    X rejected         measured as not AI tone; counted, never edited

Reference values come from the two-round study in RESEARCH.md, which measured CHINESE corpora.
They indicate direction, not calibrated English thresholds. Values marked [tunable] need
recalibration on an English corpus (scripts/compare-human-ai.py).
"""
import argparse
import json
import re
import sys
from pathlib import Path

EXTS = {".md", ".txt"}
I = "(?i)"

# (grade, name, pattern, reference per 1k words from the Chinese study, advice)
REGEX_HITS = [
    ("A", "Contrast reversal",
     I + r"\b(?:not (?:just |only |merely |simply )?|isn't |aren't |wasn't |weren't |never )"
         r"[^.!?;\n]{1,60}?[,;—]?\s*\b(?:but|rather|it's|it is|they're|they are)\b(?! also)"
         r"|\b(?:is|are|was|were) not\b[^.!?\n]{1,80}?\.\s+(?:it|they|this|that)(?:'s| is| are| was| were)\b"
         r"|\b(?:isn't|aren't|wasn't|weren't)\b[^.!?\n]{1,80}?\.\s+(?:it|they|this|that)(?:'s| is| are| was| were)\b"
         r"|\bless about\b[^.!?\n]{1,50}?\bthan\b"
         r"|\byou (?:might|may) think\b[^.!?\n]{1,60}?\b(?:but|actually|in fact)\b",
     "0.22", "State the claim directly; drop the straw-man half. Rule 1"),
    ("A", "Cue-phrase colon",
     I + r"\b(?:in short|in a nutshell|in summary|to sum up|bottom line|the key(?: point| insight| takeaway)?(?: is)?"
         r"|the core(?: idea| issue)?(?: is)?|the reasons?(?: is| are)?|the problem(?: is)?|the answer(?: is)?"
         r"|the truth(?: is)?|the point(?: is)?|the takeaway|the upshot|here's the thing|here's why"
         r"|in other words|that is|specifically|for example|my (?:view|take|conclusion|advice))\s*:"
         # cue noun announcing a verdict: "The technical reason is actually simple:", "This is a deeper problem:"
         r"|\b(?:the|a|an)\s+(?:[\w-]+\s){0,2}?(?:key|core|reason|problem|answer|truth|point|lesson|catch"
         r"|fact|reality|pattern|insight)\b[^:.!?\n\"“]{0,25}:(?!//)",
     "0.08", "Drop the cue and write the content; if the clause links back, change only the punctuation. Rule 2"),
    ("A", "Opening formula",
     I + r"\b(?:to put it bluntly|let's be honest|let me be blunt|simply put|put simply|here's the thing"
         r"|long story short|bottom line first|spoiler)\s*[,—]",
     "0.008", "Delete; state the judgment. Rule 3"),
    ("A", "Topic-shell frame",
     I + r"\b(?:when it comes to|in terms of|as for|with regard to|with respect to|in the context of|as far as [^,.\n]{2,30} (?:is|are) concerned)\b",
     "—", "Make the topic the subject; delete the shell. Rule 4"),
    ("A", "Sentence-initial connective",
     I + r"(?:^|(?<=[.!?]\s))\s{0,3}(?:however|therefore|moreover|furthermore|additionally|in addition|consequently"
         r"|thus|meanwhile|in other words|ultimately|overall|importantly|notably|crucially)\s*,",
     "—", "Move it after the subject, use a plainer word (but, so), or drop it. Rule 4"),
    ("B", "Serial list ≥3",
     r"\b[\w'-]+(?: [\w'-]+){0,3}, [\w'-]+(?: [\w'-]+){0,3}, (?:and |or )?[\w'-]+(?: [\w'-]+){0,3}",
     "1.78", "Summarize if you can; if every item must stay, change the syntax of one. Rule 5"),
    ("H", "Personifying metaphor",
     I + r"\b(?:like|as if it were|acts as|serves as|think of it as)\s+(?:a|an|your)\s+(?:[\w-]+\s){0,3}?"
         r"(?:mentor|secretary|assistant|advisor|adviser|butler|reviewer|intern|strategist|coach|partner"
         r"|expert|navigator|lighthouse|guardian|teammate|colleague|copilot|guide)\b",
     "0.002", "If asked: say what the thing actually does. Rule 7"),
    # ---- Rejected: counted and shown, explicitly do-not-edit, to prevent over-cleaning ----
    ("X", "Vague summary (rejected)",
     I + r"\b(?:significantly|dramatically|substantially|greatly|vastly|markedly)\s+"
         r"(?:improv|increas|enhanc|boost|reduc|decreas|cut|rais)\w*|\bcountless\b|\bnumerous\b|\bmassive amounts? of\b",
     "—", "Symmetric recheck 2026-10-13: net zero (vaguer 24.7% vs more specific 26.0%). Do not edit, even beside concrete numbers"),
    ("X", "Ordinal subheading (rejected)",
     I + r"^\s{0,3}#{1,6}\s{0,3}(?:\d+[.)]|[IVX]+\.|(?:first|second|third|fourth|fifth|finally)\b)",
     "—", "Humans use it more (8.6% vs 4.9%). Do not edit"),
    ("X", '"This means" restatement (rejected)',
     I + r"\b(?:this|that|which) (?:means|shows|suggests|indicates|tells us)\b",
     "—", "Humans use it more on all three measures. Do not edit"),
    ("X", "Empty lead-in to list (rejected)",
     r"[^.!?\n]{0,60}:\s*$",
     "—", "Humans use it an order of magnitude more (normal in long catalogue-style pieces). Do not edit"),
]

# Counted over the whole text, not per line
CHAR_HITS = [
    ("F", "Em dash", r"—| -- ", "0.80", ">2/1k words: handle first; suggest fixing safe local uses, justify any kept"),
    ("F", "Semicolon", r";", "—", "GPT fingerprint (δ+0.80); split when safe, justify any kept"),
    ("F", "Quotation marks", r"“|(?<!\w)\"(?=\w)", "—", "Opus uses fewer (δ−0.67); report only"),
]

# Synonym-rotation groups (heuristic for avoiding repetition; grade B)
SYN_GROUPS = [
    ("use", "utilize", "leverage", "employ", "harness"),
    ("method", "approach", "strategy", "technique", "mechanism"),
    ("improve", "enhance", "boost", "strengthen", "optimize", "elevate"),
    ("show", "reveal", "indicate", "demonstrate", "highlight", "underscore"),
    ("important", "crucial", "critical", "vital", "essential", "pivotal"),
    ("problem", "challenge", "issue", "pain point", "hurdle"),
    ("help", "assist", "empower", "support", "enable"),
]

# Thresholds [tunable] — from the Chinese study; ponytail: uncalibrated for English, rerun compare-human-ai.py on an English corpus
TH_SENT_CV = 0.55      # sentence-length CV below → uniform rhythm
TH_SECT_CV = 0.45      # section-length CV below → uniform sections
TH_HEAD_KK = 0.50      # headings per 1k words above → split too finely
TH_ISO_100P = 8.0      # isomorphic pairs per 100 paras above → too many

# Human/AI medians from the 270 matched pairs (Chinese corpus)
HUMAN_REF = {
    "Sentence-length CV": {"ref": "0.54", "ai": "0.46"},
    "Section-length CV": {"ref": "0.83", "ai": "0.31"},
    "Headings per 1k words": {"ref": "0.32", "ai": "1.26"},
    "Isomorphic pairs per 100 paras": {"ref": "5.52", "ai": "8.71"},
    "Isomorphic triples per 100 paras": {"ref": "0.41*", "ai": "0.84*"},
    "MTLD (rough)": {"ref": "143", "ai": "227"},
}

# ---------------- Splitting ----------------

HEADING = re.compile(r"^#{1,6}\s")
BOLD_LINE = re.compile(r"^\*\*[^*]{2,60}\*\*$")
LIST_LINE = re.compile(r"^\s{0,3}(?:[-*+]|\d+[.)])\s")
QUOTE_LINE = re.compile(r"^>")
FENCE = re.compile(r"^```")
TABLE_LINE = re.compile(r"^\|")
WORD = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")


def words(s):
    return WORD.findall(s)


def nwords(s):
    return len(words(s))


def split_sents(para):
    return [s.strip() for s in re.split(r"(?<=[.!?;])\s+|\n", para) if nwords(s) >= 3]


def signature(sent):
    """Sentence-structure signature: comma count, colon, parenthesis, length bucket (8 words)."""
    return (sent.count(","), ":" in sent, "(" in sent, nwords(sent) // 8)


def _iso_runs(sents, n):
    sents = [s for s in sents if nwords(s) > 6]
    for i in range(len(sents) - n + 1):
        sigs = [signature(s) for s in sents[i:i + n]]
        if all(s == sigs[0] for s in sigs) and sigs[0][0] >= 1:
            yield sents[i:i + n]


def isomorphic_triples(text):
    """Triple candidates pre-filtered by signature (wide); the model applies the "highly isomorphic"
    criterion. Wide threshold has no discriminative power (AI 71.1% vs human 56.2%); only the
    highly-isomorphic tier differs (2.76×)."""
    return [{"line": no, "sents": run}
            for kind, body, no in paragraph_blocks(text) if kind == "prose"
            for run in _iso_runs(split_sents(body), 3)]


def isomorphic_hits(para, n):
    return [" / ".join(run) for run in _iso_runs(split_sents(para), n)]


def paragraph_blocks(text):
    """Split on blank lines and classify; returns [(kind, block_text, first_line_no)]."""
    blocks, cur, cur_kind, start = [], [], None, None
    in_fence = False
    for no, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            cur.append(line)
            continue
        if not in_fence and not line.strip():
            if cur:
                blocks.append((cur_kind or "prose", "\n".join(cur), start))
                cur, cur_kind, start = [], None, None
            continue
        if not cur:
            start = no
        cur.append(line)
        if in_fence:
            cur_kind = cur_kind or "code"
        elif HEADING.match(line):
            cur_kind = "heading"
        elif QUOTE_LINE.match(line):
            cur_kind = cur_kind or "quote"
        elif TABLE_LINE.match(line):
            cur_kind = cur_kind or "table"
        elif LIST_LINE.match(line):
            cur_kind = cur_kind or "list"
        elif BOLD_LINE.match(line) and cur_kind is None:
            cur_kind = "heading"
    if cur:
        blocks.append((cur_kind or "prose", "\n".join(cur), start))
    return blocks


def mtld(toks, threshold=0.72, min_len=10):
    """Approximate MTLD lexical diversity over lowercase words."""
    if len(toks) < min_len * 4:
        return None

    def pass_factors(seq):
        factors, types, count = 0.0, set(), 0
        for t in seq:
            count += 1
            types.add(t)
            if count >= min_len and len(types) / count <= threshold:
                factors += 1
                types, count = set(), 0
        if count:
            factors += (1 - len(types) / count) / (1 - threshold)
        return max(factors, 1e-9)

    f, r = pass_factors(toks), pass_factors(toks[::-1])
    return round(len(toks) / 2 * (1 / f + 1 / r))


def cv(vals):
    if len(vals) < 2:
        return None
    m = sum(vals) / len(vals)
    if m == 0:
        return None
    return (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5 / m


def syn_present(word, body):
    """Base form plus simple inflections (s/es/ed/d/ing, e-dropping)."""
    stem = word[:-1] if word.endswith("e") else word
    return re.search(rf"(?i)\b(?:{word}|{stem}(?:es|ed|ing|s|d)|{word}s)\b", body)


# ---------------- Metrics ----------------

def measure_docs(docs):
    total_words = 0
    regex_hits = {name: [] for _, name, *_ in REGEX_HITS}
    char_counts = {name: 0 for _, name, *_ in CHAR_HITS}
    syn_hits = []
    n_para = n_head = iso2 = iso3 = 0
    sent_lens, sect_lens, all_words = [], [], []

    for fname, text in docs:
        in_fence = False
        for no, line in enumerate(text.splitlines(), 1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for _, name, pat, *_ in REGEX_HITS:
                for m in re.finditer(pat, line):
                    regex_hits[name].append({"file": fname, "line": no, "excerpt": m.group(0)[:100]})
        for _, name, pat, *_ in CHAR_HITS:
            char_counts[name] += len(re.findall(pat, text))

        blocks = paragraph_blocks(text)
        sect = 0
        for kind, body, no in blocks:
            if kind == "heading":
                n_head += 1
                if sect:
                    sect_lens.append(sect)
                sect = 0
                continue
            if kind != "prose":
                continue
            n_para += 1
            sect += nwords(body)
            sent_lens.extend(nwords(s) for s in split_sents(body))
            iso2 += len(isomorphic_hits(body, 2))
            iso3 += len(isomorphic_hits(body, 3))
            all_words.extend(w.lower() for w in words(body))
            for group in SYN_GROUPS:
                found = [w for w in group if syn_present(w, body)]
                if len(found) >= 2:
                    syn_hits.append({"file": fname, "line": no, "excerpt": " / ".join(found),
                                     "context": body[:120]})
        if sect:
            sect_lens.append(sect)
        total_words += nwords(text)

    kk = total_words / 1000 or 1
    sent_cv = cv(sent_lens) if sent_lens else None
    sect_cv = cv(sect_lens) if len(sect_lens) >= 3 else None
    return {
        "meta": {"docs": len(docs), "words": total_words, "paragraphs": n_para, "headings": n_head},
        "density": {nm: round(len(regex_hits[nm]) / kk, 3) for _, nm, *_ in REGEX_HITS},
        "char_density": {nm: round(n / kk, 3) for nm, n in char_counts.items()},
        "hits": regex_hits,
        "syn_hits": syn_hits,
        "structure": {
            "Sentence-length CV": round(sent_cv, 3) if sent_cv else None,
            "Section-length CV": round(sect_cv, 3) if sect_cv else None,
            "Headings per 1k words": round(n_head / kk, 3),
            "Isomorphic pairs per 100 paras": round(iso2 / n_para * 100, 2) if n_para else None,
            "Isomorphic triples per 100 paras": round(iso3 / n_para * 100, 2) if n_para else None,
            "MTLD (rough)": mtld(all_words),
        },
    }


# ---------------- Semantic-layer candidates ----------------

NOISE_RE = re.compile(r"\]\(|\]\s*\(|\||^!")
CAND_CAPS = {"rename": 60, "cohesion": 60, "colon": 80, "iso3": 60}  # long-doc caps; overflow sampled and flagged


def clean_para(b):
    """Strip markdown emphasis/links; noise blocks (nav/tables/images) return empty."""
    if NOISE_RE.search(b[:200]):
        return ""
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", b)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    return re.sub(r"[*`_#>]", "", t).strip()


def extract_candidates(docs):
    """Four candidate types; the model writes label/confidence/reason back into each entry."""
    rename, cohesion, colon, iso3 = [], [], [], []
    for fname, text in docs:
        blocks = [(clean_para(b), no) for kind, b, no in paragraph_blocks(text) if kind == "prose"]
        blocks = [(b, no) for b, no in blocks if nwords(b) >= 15]
        rename += [{"type": "rename", "file": fname, "line": no, "para": b}
                   for b, no in blocks if nwords(b) >= 25]
        for (a, _), (b, no) in zip(blocks, blocks[1:]):
            tail = split_sents(a) or [a[-120:]]
            head = split_sents(b) or [b[:120]]
            cohesion.append({"type": "cohesion", "file": fname, "line": no,
                             "prev_tail": tail[-1], "next_head": head[0]})
        in_fence = False
        for no, line in enumerate(text.splitlines(), 1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence or HEADING.match(line) or LIST_LINE.match(line) or NOISE_RE.search(line):
                continue
            for m in re.finditer(r"([^:,.!?\n]{2,60}):(?!//)\s*(.{2,100})", line):
                colon.append({"type": "colon", "file": fname, "line": no,
                              "colon_before": m.group(1), "colon_after": m.group(2),
                              "sentence": line.strip()[:200]})
        iso3 += [dict(c, file=fname) for c in isomorphic_triples(text)]

    all_c = {"rename": rename, "cohesion": cohesion, "colon": colon, "iso3": iso3}
    meta = {"n_candidates": sum(min(len(v), CAND_CAPS[k]) for k, v in all_c.items())}
    meta.update({f"n_{k}": len(v) for k, v in all_c.items()})
    over = {k: cap for k, cap in CAND_CAPS.items() if len(all_c[k]) > cap}
    meta["truncated"] = over or False
    for k, cap in over.items():  # uniform sampling, not head-biased
        step = len(all_c[k]) / cap
        all_c[k] = [all_c[k][int(i * step)] for i in range(cap)]
    return {"meta": meta, **all_c}


# ---------------- Text report ----------------

def fmt_report(r, max_hits):
    m = r["meta"]
    out = ["Less AI tone detection report (detect only, no rewriting)", "",
           f"Corpus: {m['docs']} docs / {m['words']} words / {m['paragraphs']} paragraphs / {m['headings']} headings",
           "References come from a Chinese-corpus study: direction only, not English-calibrated.", ""]

    titles = {"A": "Mechanical-fix candidates (model reviews; edit after user reply)",
              "B": "Suggested-fix candidates (model filters each; edit after user reply)",
              "H": "Human-review zone (kept by default; only if the user asks)",
              "X": "Rejected features (not AI tone; counts only, do not edit)"}
    for level, title in titles.items():
        sec = []
        for lv, nm, _, ref, adv in REGEX_HITS:
            hits = r["hits"].get(nm, [])
            if lv != level or not hits:
                continue
            ref_s = f" (ref ≈{ref}/1k)" if ref != "—" else ""
            sec += [f"  {nm}: {len(hits)} hits, {r['density'][nm]}/1k words{ref_s}", f"    → {adv}"]
            sec += [f"      · {h['file']}:{h['line']}  {h['excerpt']}" for h in hits[:max_hits]]
        if sec:
            out += [f"[{level}] {title}", *sec, ""]

    out.append("[F] Fingerprints (per-model; read with direction)")
    for _, nm, _, ref, adv in CHAR_HITS:
        out += [f"  {nm}: {r['char_density'][nm]}/1k words" + (f" (ref ≈{ref})" if ref != "—" else ""),
                f"    → {adv}"]
    out.append("")

    if r["syn_hits"]:
        out.append("[B] Synonym rotation (heuristic; false positives likely; review each)")
        for h in r["syn_hits"][:max_hits * 2]:
            out += [f"  · {h['file']}:{h['line']}  rotation: {h['excerpt']}", f"    {h['context']}"]
        out.append("")

    s = r["structure"]
    checks = [("Sentence-length CV", lambda v: v < TH_SENT_CV, "low = uniform rhythm"),
              ("Section-length CV", lambda v: v < TH_SECT_CV, "low = uniform sections"),
              ("Headings per 1k words", lambda v: v > TH_HEAD_KK, "high = split too finely"),
              ("Isomorphic pairs per 100 paras", lambda v: v > TH_ISO_100P, "high"),
              ("Isomorphic triples per 100 paras", lambda v: v > 0.8, "high; see criteria file")]
    out.append("[C] Structure and rhythm (flagged only when off the reference in the noted direction)")
    flags = [f"  ⚠ {k}={s[k]} (human {HUMAN_REF[k]['ref']} / AI {HUMAN_REF[k]['ai']}; {note})"
             for k, bad, note in checks if s[k] is not None and bad(s[k])]
    out += flags or ["  (all within reference ranges)"]
    if s["MTLD (rough)"]:
        ref = HUMAN_REF["MTLD (rough)"]
        out.append(f"  MTLD (rough)={s['MTLD (rough)']} (human ≈{ref['ref']} / AI ≈{ref['ai']}; "
                   "higher = avoids repetition; scale differs across languages)")
    out += ["", "Order: A, then B. C needs structural changes; only if the user asks."]
    return "\n".join(out)


def load_docs(p):
    if p.is_file():
        return [(p.name, p.read_text(encoding="utf-8", errors="ignore"))]
    return [(str(f.relative_to(p)), f.read_text(encoding="utf-8", errors="ignore"))
            for f in sorted(p.rglob("*")) if f.suffix.lower() in EXTS and f.is_file()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="file or directory")
    ap.add_argument("--json", action="store_true", help="output JSON")
    ap.add_argument("--max-hits", type=int, default=5, help="max hits listed per item")
    ap.add_argument("--candidates", action="store_true", help="extract semantic-layer candidates instead")
    ap.add_argument("--out", help="candidate JSON path (default: stdout)")
    args = ap.parse_args()

    p = Path(args.target)
    if not p.exists():
        sys.exit(f"Path does not exist: {p}")
    docs = load_docs(p)
    if not docs:
        sys.exit("No .md/.txt files found")

    if args.candidates:
        c = extract_candidates(docs)
        payload = json.dumps(c, ensure_ascii=False, indent=1)
        if not args.out:
            print(payload)
            return
        Path(args.out).write_text(payload, encoding="utf-8")
        mm = c["meta"]
        print(f"{mm['n_candidates']} candidates → {args.out} (rename {mm['n_rename']} / cohesion "
              f"{mm['n_cohesion']} / colon {mm['n_colon']} / iso3 {mm['n_iso3']})")
        return

    r = measure_docs(docs)
    if r["meta"]["words"] < 300:
        sys.exit("Too few words (<300); detection is meaningless")
    print(json.dumps(r, ensure_ascii=False, indent=1) if args.json else fmt_report(r, args.max_hits))


if __name__ == "__main__":
    main()
