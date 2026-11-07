#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Single-file or directory "less AI tone" detection report (step 1 of v2: detect only, no rewriting).

Usage:
    python3 scripts/detect.py <file-or-dir> [--json] [--max-hits 5]
    python3 scripts/detect.py <file> --candidates [--out candidates.json]

--candidates extracts semantic-layer candidates (synonym-renaming paragraphs / inter-paragraph cohesion
interfaces / colon sentences / triple isomorphism). The in-session Claude judges them per
references/semantic-criteria.md; results are merged into the report.

Grades:
    A mechanical fix   fixed sentence-pattern / punctuation issues; model reviews and suggests; edit after user reply
    B suggested fix    needs sentence restructuring or rewording; model reviews each item; edit after user reply
    C report only      structure/rhythm distribution features; not edited by default
    F fingerprint      per-model features (em dash / semicolon / quotation marks); must be read with direction

Human reference values come from two rounds of measurement (see RESEARCH.md):
- Round 1: 629-doc comparison (5 models x 60 docs vs 329 human docs; unpaired)
- Round 2: 270 matched pairs (same topic, same facts) + 430k semantic judgments
Thresholds marked [tunable] are empirical; recalibrate when the corpus changes.
"""
import argparse
import json
import re
import sys
from pathlib import Path

EXTS = {".md", ".txt"}

# ---------------- Regex indicators (level, name, pattern, human ref per 1k chars, advice) ----------------

REGEX_HITS = [
    ("A", "Contrast reversal",
     r"(?:不是|并非|不在于|与其说)[^，。！？\n]{1,20}[，]?(?:而是|而在于|不如说)",
     "0.22", "State directly: drop 「不是A」 and give B. See rule 1"),
    ("A", "Cue-phrase colon",
     r"(?:一句话(?:总结|说|概括)|简单说|说白了|总结|小结|结论|核心(?:是|在于|观点)?"
     r"|关键(?:是|在于)?|重点(?:是)?|原因(?:如下|有|在于)?|问题(?:是|在于)?"
     r"|答案(?:是)?|本质(?:是|上)?|具体(?:来说|如下|包括)?"
     r"|举例(?:来说)?|换句话说|也就是说|我的(?:观点|判断|结论)|建议(?:是)?)[：:]",
     "0.08", "Drop the cue phrase and write the content; if the first half continues the prior sentence, change only the punctuation. See rule 2"),
    ("A", "Opening formula",
     r"(?:说白了|说穿了|先说结论)[，,]",
     "0.008", "Delete; state the judgment directly. See rule 3"),
    ("A", "当…时 clause",
     r"当[^，。\n]{2,20}(?<!的时候)时，",
     "—", "Delete 当 and 时 so the clause serves directly as the preceding clause. See rule 4"),
    ("A", "Topic-shell frame",
     r"(?:对于[^，。\n]{2,15}来说|对[^，。\n]{2,15}而言|就[^，。\n]{2,15}而言|在[^，。\n]{2,12}方面)",
     "—", "Put the object directly in subject position; delete the shell. See rule 4"),
    ("A", "Sentence-initial connective",
     r"(?:^|\n)\s{0,3}(?:然而|因此|此外|与此同时|换言之|总而言之)[，、]",
     "—", "Move after the subject, or use 不过 / 其实 (but / actually). See rule 4"),
    ("B", "Enumeration comma list ≥3",
     r"[^，。！？；：、\n]{1,14}、[^，。！？；：、\n]{1,14}、[^，。！？；：、\n]{1,14}",
     "1.78", "Summarize if possible; if all items must stay, break the syntax of one of them. See rule 5"),
    ("B", "Long pre-modifier",
     r"(?:一个|一种|一套|这种|这个)[^，。、；：！？\n]{15,}的[一-鿿]{2,5}",
     "0.1", "Split into two clauses (two or more chained 的 count the same). See rule 4"),
    ("H", "Personifying metaphor",
     r"(?:像|如同|好比|犹如|相当于)[^，。！？\n]{0,6}一[位名个][^，。！？\n]{0,14}"
     r"(?:导师|秘书|助手|顾问|管家|审查员|实习生|军师|教练|伙伴|专家|舵手|灯塔)",
     "0.002", "Replace with what the thing actually does. See rule 6"),
    ("X", "Vague summary (rejected)",
     r"(?:显著(?:提升|提高|增长|改善|增加|优势)|大幅(?:提升|增长|提高|改善|下降|减少)"
     r"|明显(?:改善|提升|优势|变化)|效率的提升|众多|海量)",
     "—", "Symmetric recheck on 2026-10-13: net zero (AI vaguer 24.7% vs more specific 26.0%; numbers kept 98%), "
     "do not edit even when the same paragraph has concrete numbers; fidelity in rewrites is covered by the information-conservation principle"),
    # ---- Rejected features: counted and shown, explicitly marked do-not-edit, to prevent over-cleaning ----
    ("X", "Ordinal subheading (rejected)",
     r"(?:^|\n)\s{0,3}#{1,6}\s{0,3}[一二三四五六七八九十][、.]",
     "—", "Measured: humans use it more than AI (8.6% vs 4.9%); not an AI-tone feature; do not edit"),
    ('X', '"This means" restatement (rejected)',
     r"(?:这意味着|这表明|这说明)",
     "—", "Matched-pair retest: humans use it more; all three measures point the opposite way; do not edit"),
    ("X", "Empty lead-in to list (rejected)",
     r"[^，。！？\n]{0,25}[：:]\s*(?:\n|$)",
     "—", "Matched-pair retest: humans are an order of magnitude higher (normal style for catalogue-like long texts); do not edit"),
]

# Em dash / semicolon / quotation marks are counted per character, not per line
CHAR_HITS = [
    ("F", "Em dash", "——", "0.80", "Density >2/1k chars: handle first; safe local uses are suggested for change by default; if kept, state its function"),
    ("F", "Semicolon", "；", "—", "GPT fingerprint (δ+0.80); when safely splittable, suggest splitting by default; if kept, state the hierarchical role"),
    ("F", "Quotation marks", "“", "—", "Opus uses fewer (δ−0.67); fewer quotes is not necessarily a problem; report only"),
]

# Synonym-rotation groups (heuristic for avoiding word repetition; grade B)
SYN_GROUPS = [
    ("使用", "采用", "运用", "利用", "借助"),
    ("方法", "方式", "途径", "路径", "做法"),
    ("提升", "提高", "增强", "强化", "优化"),
    ("显示", "表明", "揭示", "反映", "说明"),
    ("重要", "关键", "核心", "至关重要"),
    ("问题", "难题", "挑战", "困境", "痛点"),
    ("帮助", "协助", "助力", "支持"),
]

# Thresholds [tunable]: recalibrate when the corpus changes
TH_SENT_CV = 0.55      # sentence-length CV below this → rhythm too uniform (v1 measured: human 0.67 / AI 0.58)
TH_SECT_CV = 0.45      # section-length CV below this → section lengths too uniform
TH_HEAD_KK = 0.50      # headings per 1k chars above this → split too finely
TH_ISO_100P = 8.0      # isomorphic pairs per 100 paras above this → too many (human 4.81 / AI 9.41)

# Human reference lines (median of 270 matched-pair measurements; see Downloads/分析结果/配对指标结果-按模型分列.csv).
# ref looks like "0.80" (human median per 1k chars) or "4.81/AI9.41"; deviation counts on both sides (two-sided scoring).
HUMAN_REF = {
    "Sentence-length CV":  {"ref": "0.54",  "ai": "0.46",  "note": "humans vary sentence length; below reference = uniform rhythm", "direction": "low"},
    "Section-length CV":   {"ref": "0.83",  "ai": "0.31",  "note": "human section lengths vary; below reference = all sections equal length", "direction": "low"},
    "Headings per 1k chars": {"ref": "0.32", "ai": "1.26", "note": "humans write whole pieces continuously; above reference = split too finely", "direction": "high"},
    "Isomorphic pairs per 100 paras": {"ref": "5.52", "ai": "8.71", "note": "layer-1 indicator 4 (two-sentence version), medium effect", "direction": "high"},
    "Isomorphic triples per 100 paras": {"ref": "0.41*", "ai": "0.84*", "note": "*heuristic estimate; semantic judgment in the criteria file", "direction": "high"},
    "MTLD (rough)":        {"ref": "143",   "ai": "227",   "note": "high = varied wording; AI above human = avoids repetition", "direction": "high"},
    "Em dash":             {"ref": "0.83",  "ai": "2.02",  "note": "Opus fingerprint +0.95 / GPT −0.54, opposite directions", "direction": "per-model"},
    "Semicolon":           {"ref": "0.77",  "ai": "1.51",  "note": "GPT fingerprint δ+0.80; Opus −0.11, no difference", "direction": "per-model"},
    "Quotation marks":     {"ref": "20.0",  "ai": "2.7",   "note": "Opus uses fewer δ−0.67; report only, do not edit", "direction": "low"},
    "Enumeration comma":   {"ref": "6.12",  "ai": "8.24",  "note": "layer-1 dense enumeration (many items packed into one sentence)", "direction": "high"},
    "Colon":               {"ref": "3.59",  "ai": "2.70",  "note": "humans use more colons overall; only the conclusion-cue subtype is a real signal, judged at semantic layer", "direction": "low"},
}

# ---------------- Splitting ----------------

HEADING = re.compile(r"^#{1,6}\s")
BOLD_LINE = re.compile(r"^\*\*[^*]{2,40}\*\*$")
LIST_LINE = re.compile(r"^\s{0,3}(?:[-*+]|\d+[.、)])\s")
QUOTE_LINE = re.compile(r"^>")
FENCE = re.compile(r"^```")
TABLE_LINE = re.compile(r"^\|")

COMMENT = re.compile(
    r"^(?:听起来|看起来|看上去|听上去|说白了|说到底|换句话说|意味着|值得注意|"
    r"不难看出|细看|再看|回过头看|问题在于|原因在于|结果是|有意思的是|"
    r"更重要的是|关键在于|真正的)")


def hanzi(s):
    return len(re.findall(r"[一-鿿]", s))


def split_sents(para):
    return [s.strip() for s in re.split(r"[。！？；]", para) if len(s.strip()) >= 4]


def signature(sent):
    """Sentence-structure signature: comma count, colon present, bracket present, length bucket (from v1, kept after retest)."""
    return (sent.count("，"), "：" in sent or ":" in sent,
            ("（" in sent or "(" in sent), len(sent) // 15)


def isomorphic_triples(text):
    """Triple-isomorphism candidates (for semantic judgment): runs of three sentences pre-filtered by signature.
    Each carries its line number and the three sentences. The pre-filter is wide (partial isomorphism included);
    Claude tightens it with the "highly isomorphic" criterion. 270-pair measurement: at the wide threshold
    AI 71.1% vs human 56.2% has no discriminative power; only the highly-isomorphic tier differs (2.76×)."""
    out = []
    for kind, body, first_no in paragraph_blocks(text):
        if kind != "prose":
            continue
        sents = [s for s in split_sents(body) if len(s) > 10]
        for i in range(len(sents) - 2):
            sigs = [signature(s) for s in sents[i:i + 3]]
            if all(s == sigs[0] for s in sigs) and sigs[0][0] >= 1:
                out.append({"line": first_no,
                            "sents": sents[i:i + 3]})
    return out


def isomorphic_hits(para, n):
    sents = [s for s in split_sents(para) if len(s) > 10]
    hits = []
    for i in range(len(sents) - n + 1):
        sigs = [signature(s) for s in sents[i:i + n]]
        if all(s == sigs[0] for s in sigs) and sigs[0][0] >= 1:
            hits.append("／".join(sents[i:i + n]))
    return hits


def paragraph_blocks(text):
    """Split on blank lines and classify blocks; returns [(kind, block_text, first_line_no)]."""
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
    """Approximate MTLD (lexical diversity). Chinese has no word segmentation, so 2-char bigrams stand in as pseudo-words; rough."""
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
    var = sum((v - m) ** 2 for v in vals) / len(vals)
    return (var ** 0.5) / m


# ---------------- Metrics ----------------

def measure_docs(docs):
    total_han = 0
    regex_hits = {name: [] for _, name, *_ in REGEX_HITS}
    char_counts = {name: 0 for _, name, *_ in CHAR_HITS}
    syn_hits = []
    n_para = n_head = 0
    iso2 = iso3 = 0
    sent_lens, sect_lens = [], []
    all_bigrams = []

    for fname, text in docs:
        lines = text.splitlines()
        # Per-line regex hits (skip code fences)
        in_fence = False
        for no, line in enumerate(lines, 1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for _, name, pat, *_ in REGEX_HITS:
                for m in re.finditer(pat, line):
                    excerpt = m.group(0)
                    regex_hits[name].append(
                        {"file": fname, "line": no, "excerpt": excerpt[:60]})
        for _, name, ch, *_ in CHAR_HITS:
            char_counts[name] += text.count(ch)

        # Structure
        blocks = paragraph_blocks(text)
        sect_chars = 0
        for kind, body, first_no in blocks:
            if kind == "heading":
                n_head += 1
                if sect_chars > 0:
                    sect_lens.append(sect_chars)
                sect_chars = 0
                continue
            if kind != "prose":
                continue
            n_para += 1
            h = hanzi(body)
            sect_chars += len(body)
            for s in split_sents(body):
                sent_lens.append(hanzi(s) or len(s))
            iso2 += len(isomorphic_hits(body, 2))
            iso3 += len(isomorphic_hits(body, 3))
            all_bigrams.extend(
                body[i:i + 2] for i in range(len(body) - 1) if hanzi(body[i:i + 2]) == 2)
        if sect_chars > 0:
            sect_lens.append(sect_chars)

        # Synonym rotation (≥2 distinct members in one paragraph)
        for kind, body, first_no in blocks:
            if kind != "prose":
                continue
            for group in SYN_GROUPS:
                found = [w for w in group if w in body]
                if len(found) >= 2:
                    syn_hits.append({"file": fname, "line": first_no,
                                     "excerpt": "／".join(found),
                                     "context": body[:70]})
        total_han += hanzi(text)

    kk = total_han / 1000 or 1
    sent_cv = cv(sent_lens) if sent_lens else None
    sect_cv = cv(sect_lens) if len(sect_lens) >= 3 else None

    return {
        "meta": {
            "docs": len(docs), "han_10k": round(total_han / 10000, 2),
            "paragraphs": n_para, "headings": n_head,
        },
        "density": {name: round(n / kk, 3) for name, n in
                    [(nm, len(v)) for _, nm, *_ in REGEX_HITS for v in [regex_hits[nm]]]},
        "char_density": {name: round(n / kk, 3) for name, n in char_counts.items()},
        "hits": regex_hits,
        "syn_hits": syn_hits,
        "structure": {
            "Sentence-length CV": round(sent_cv, 3) if sent_cv else None,
            "Section-length CV": round(sect_cv, 3) if sect_cv else None,
            "Headings per 1k chars": round(n_head / kk, 3),
            "Isomorphic pairs per 100 paras": round(iso2 / n_para * 100, 2) if n_para else None,
            "Isomorphic triples per 100 paras": round(iso3 / n_para * 100, 2) if n_para else None,
            "MTLD (rough)": mtld(all_bigrams),
        },
    }


# ---------------- Semantic-layer candidate extraction ----------------

def first_prose_blocks(text, max_gap=2):
    """Prose blocks split on blank lines, with headings/code/tables dropped. (max_gap is accepted but unused.)"""
    return [(b, n) for kind, b, n in paragraph_blocks(text) if kind == "prose"]


NOISE_RE = re.compile(r"\]\(|\]\s*\(|\||^!|^中文\s*\|")


def clean_para(b):
    """Strip markdown emphasis/link syntax and return plain text; noise lines (nav/tables/images) return empty."""
    if NOISE_RE.search(b[:200]):
        return ""
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", b)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[*`_#>]", "", t)
    return t.strip()


CAND_CAPS = {"rename": 60, "cohesion": 60, "colon": 80, "iso3": 60}  # caps for long docs; overflow is truncated and flagged


def extract_candidates(docs):
    """Four kinds of semantic-layer candidates. Each carries its criterion type. The in-session Claude
    judges each one closed-set per references/semantic-criteria.md (label + confidence) and writes results
    back into the same JSON structure in the label/confidence/reason fields."""
    rename, cohesion, colon, iso3 = [], [], [], []
    for fname, text in docs:
        blocks = [(clean_para(b), no) for b, no in first_prose_blocks(text)]
        blocks = [(b, no) for b, no in blocks if hanzi(b) >= 20]
        # 1) Synonym renaming: paragraph level (one candidate per paragraph; judge how many substantive rewordings)
        for b, no in blocks:
            if hanzi(b) >= 30:
                rename.append({"type": "rename", "file": fname, "line": no, "para": b})
        # 2) Cohesion chain: inter-paragraph interface (last sentence of previous para + first of next)
        for i in range(len(blocks) - 1):
            a, b = blocks[i][0], blocks[i + 1][0]
            tail = split_sents(a) or [a[-60:]]
            head = split_sents(b) or [b[:60]]
            cohesion.append({"type": "cohesion",
                             "file": fname, "line": blocks[i + 1][1],
                             "prev_tail": tail[-1], "next_head": head[0]})
        # 3) Colon sentences: body colons (excluding quotes, headings, list lines)
        in_fence = False
        for no, line in enumerate(text.splitlines(), 1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence or HEADING.match(line) or LIST_LINE.match(line) or NOISE_RE.search(line):
                continue
            for m in re.finditer(r"([^：:，。！？\n]{2,30})[：:](.{2,60})", line):
                colon.append({"type": "colon",
                              "file": fname, "line": no,
                              "colon_before": m.group(1), "colon_after": m.group(2)[:60],
                              "sentence": line.strip()[:120]})
        # 4) Triple isomorphism: signature pre-filter + Claude judges "highly isomorphic"
        iso3.extend(dict(c, file=fname) for c in isomorphic_triples(text))
    all_c = {"rename": rename, "cohesion": cohesion, "colon": colon, "iso3": iso3}
    truncated = {k: len(v) > cap for k, v, cap in
                 ((k, v, CAND_CAPS[k]) for k, v in all_c.items())}
    meta = {"n_candidates": sum(min(len(v), CAND_CAPS[k]) for k, v in all_c.items())}
    meta.update({f"n_{k}": len(v) for k, v in all_c.items()})
    meta["truncated"] = {k: cap for k, cap in CAND_CAPS.items() if truncated[k]} or False
    if meta["truncated"]:
        # Uniform sampling keeps candidates (not biased to the head); judged coverage = kept / total
        for k, cap in CAND_CAPS.items():
            if truncated[k]:
                step = len(all_c[k]) / cap
                all_c[k] = [all_c[k][int(i * step)] for i in range(cap)]
    return {"meta": meta,
            "rename": all_c["rename"], "cohesion": all_c["cohesion"],
            "colon": all_c["colon"], "iso3": all_c["iso3"]}


# ---------------- Report ----------------

def fmt_report(r, max_hits):
    out = ["Less-AI-tone detection report (v2: detect only, no rewriting)", ""]
    m = r["meta"]
    out.append(f"Corpus: {m['docs']} docs / {m['han_10k']} 10k Han chars / {m['paragraphs']} paragraphs / {m['headings']} headings")
    out.append("")

    def emit(level, title):
        rows = [(nm, ref, adv) for lv, nm, _, ref, adv in REGEX_HITS if lv == level]
        hits = r["hits"]
        dens = r["density"]
        any_row = False
        sec = [f"[{level}] {title}"]
        for nm, ref, adv in rows:
            n = len(hits.get(nm, []))
            d = dens.get(nm, 0)
            if n == 0:
                continue
            any_row = True
            ref_s = f" (human ≈{ref}/1k chars)" if ref != "—" else ""
            sec.append(f"  {nm}: {n} hits, {d}/1k chars{ref_s}")
            sec.append(f"    → {adv}")
            for h in hits[nm][:max_hits]:
                sec.append(f"      · {h['file']}:{h['line']}  {h['excerpt']}")
        if any_row:
            out.extend(sec)
            out.append("")
        return any_row

    emit("A", "Grade A candidates (suggested after model review; edit after user reply)")
    emit("B", "Grade B candidates (model filters item by item; edit after user reply)")
    emit("C", "Report only (not edited by default)")
    emit("H", "Human-review zone (kept by default; review only if the user asks)")
    emit("X", "Rejected features (measured as not AI tone; counts only, do not edit)")

    # Fingerprint
    sec = ["[F] Fingerprint (per-model features; read with direction)"]
    for _, nm, _, ref, adv in CHAR_HITS:
        d = r["char_density"].get(nm, 0)
        sec.append(f"  {nm}: {d}/1k chars" + (f" (human ≈{ref})" if ref != "—" else ""))
        sec.append(f"    → {adv}")
    out.extend(sec)
    out.append("")

    # Synonym rotation
    if r["syn_hits"]:
        out.append("[B] Word repetition avoided (synonym-rotation heuristic; false positives possible; review each)")
        for h in r["syn_hits"][:max_hits * 2]:
            out.append(f"  · {h['file']}:{h['line']}  rotation: {h['excerpt']}")
            out.append(f"    {h['context']}")
        out.append("")

    # Structure
    s = r["structure"]
    out.append("[C] Structure and rhythm (vs human reference lines; flagged only on deviation in the noted direction)")
    flags = []
    if s["Sentence-length CV"] is not None and s["Sentence-length CV"] < TH_SENT_CV:
        ref = HUMAN_REF["Sentence-length CV"]
        flags.append(f"Sentence-length CV={s['Sentence-length CV']} (human median {ref['ref']} / AI {ref['ai']}; low = uniform rhythm)")
    if s["Section-length CV"] is not None and s["Section-length CV"] < TH_SECT_CV:
        ref = HUMAN_REF["Section-length CV"]
        flags.append(f"Section-length CV={s['Section-length CV']} (human median {ref['ref']} / AI {ref['ai']}; low = uniform section lengths)")
    if s["Headings per 1k chars"] > TH_HEAD_KK:
        ref = HUMAN_REF["Headings per 1k chars"]
        flags.append(f"Headings {s['Headings per 1k chars']}/1k chars (human median {ref['ref']} / AI {ref['ai']}; high = split too finely)")
    if s["Isomorphic pairs per 100 paras"] is not None and s["Isomorphic pairs per 100 paras"] > TH_ISO_100P:
        ref = HUMAN_REF["Isomorphic pairs per 100 paras"]
        flags.append(f"Isomorphic pairs {s['Isomorphic pairs per 100 paras']}/100 paras (human {ref['ref']} / AI {ref['ai']}; high)")
    if s["Isomorphic triples per 100 paras"] and s["Isomorphic triples per 100 paras"] > 0.8:
        ref = HUMAN_REF["Isomorphic triples per 100 paras"]
        flags.append(f"Isomorphic triples {s['Isomorphic triples per 100 paras']}/100 paras (human {ref['ref']} / AI {ref['ai']}; high; see criteria file)")
    for f_ in flags:
        out.append(f"  ⚠ {f_}")
    if not flags:
        out.append("  (all structure/rhythm metrics within reference ranges)")
    if s["MTLD (rough)"]:
        ref = HUMAN_REF["MTLD (rough)"]
        out.append(f"  MTLD (rough)={s['MTLD (rough)']} (human median ≈{ref['ref']} / AI ≈{ref['ai']}; above human = avoids repetition; rough estimate, reference only)")
    out.append("")
    out.append("Suggested order: A first, then B. C-grade rewrites need structural changes or added information, "
               "which is beyond the whitelist boundary; consider only if the user explicitly asks.")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="file or directory")
    ap.add_argument("--json", action="store_true", help="output JSON")
    ap.add_argument("--max-hits", type=int, default=5, help="max hits listed per item")
    ap.add_argument("--candidates", action="store_true",
                    help="extract semantic-layer candidates (rename/cohesion/colon/iso3); skip regular detection")
    ap.add_argument("--out", help="candidate JSON output path (default: stdout)")
    args = ap.parse_args()

    p = Path(args.target)
    if not p.exists():
        print(f"Path does not exist: {p}", file=sys.stderr)
        sys.exit(1)
    docs = []
    if p.is_file():
        docs.append((p.name, p.read_text(encoding="utf-8", errors="ignore")))
    else:
        for f in sorted(p.rglob("*")):
            if f.suffix.lower() in EXTS and f.is_file():
                docs.append((str(f.relative_to(p)),
                             f.read_text(encoding="utf-8", errors="ignore")))
    if not docs:
        print("No .md/.txt files found", file=sys.stderr)
        sys.exit(1)

    if args.candidates:
        c = extract_candidates(docs)
        payload = json.dumps(c, ensure_ascii=False, indent=1)
        if args.out:
            Path(args.out).write_text(payload, encoding="utf-8")
            n = c["meta"]["n_candidates"]
            print(f"{n} candidates → {args.out}"
                  f" (rename {c['meta']['n_rename']} / cohesion {c['meta']['n_cohesion']}"
                  f" / colon {c['meta']['n_colon']} / iso3 {c['meta']['n_iso3']})")
        else:
            print(payload)
        return

    r = measure_docs(docs)
    if r["meta"]["han_10k"] < 0.05:
        print("Too few Han characters (<500); detection is meaningless", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        print(fmt_report(r, args.max_hits))


if __name__ == "__main__":
    main()
