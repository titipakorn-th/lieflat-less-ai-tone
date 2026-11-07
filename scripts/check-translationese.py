"""Frequency of translationese markers in the AI corpus (per 1k Han chars).

Usage:
    python3 scripts/check-translationese.py <corpus-dir> [more dirs...]

If the human corpus is not on this machine, only absolute AI-side rates can be reported:
a marker that is very rare in AI text cannot be a discriminating AI-tone feature.
BASELINE holds rules already confirmed to discriminate in research, measured with the same script on the same corpus, as the inclusion bar.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

MARKERS = {
    "Passive-abstract": r"被(认为|视为|称为|设计为|应用于|赋予|看作)",
    "受到…的 (subject to)": r"受到[^，。]{0,12}的(关注|影响|重视|挑战)",
    "Formal subject": r"(值得注意的是|有必要指出的是|可以说的是|需要指出的是)",
    "存在着/有着 (exist/have)": r"(存在着|有着)",
    "当…的时候 (when)": r"当[^，。]{2,20}(的时候|时)，",
    "在…的过程中 (in the course of)": r"在[^，。]{2,20}(的过程中|的情况下)",
    "如果…的话 (if…then)": r"如果[^，。]{2,20}的话",
    "Dense coordinating conjunctions": r"并且|而且",
    "Light verbs": r"(进行|作出|给予|予以)了?[^，。]{0,6}(分析|调整|优化|支持|评估|检查|讨论)",
    "不仅仅是 (not merely)": r"(不仅仅是|远不止是|不过是|无非是)",
    "正是/恰恰是 (precisely)": r"(正是|恰恰是)",
    "Literal plural": r"(一系列的|各种各样的|诸多)",
    "Literal degree expressions": r"(在某种程度上|一定程度上|从某种意义上说|在很大程度上|相对而言)",
    "Sentence-initial connective": r"(?:^|\n)\s*(然而|因此|此外|与此同时|换言之|总而言之)[，、]",
    '"This means" restatement': r"(这意味着|这表明|这说明|换句话说)",
    "Topic-shell frame": r"(对于[^，。]{2,15}来说|对[^，。]{2,15}而言|就[^，。]{2,15}而言|在[^，。]{2,12}方面)",
    "扮演角色 (play a role)": r"(扮演|承担)了?[^，。]{0,8}角色",
    "以一种…方式 (in a … way)": r"以一种[^，。]{2,12}的(方式|形式)",
    "使得…能够 (cause … to be able)": r"使得?[^，。]{0,12}(能够|可以)",
    "Long pre-modifier": r"(?:一个|一种|一套|这种|这个)[^，。、；：！？\n]{15,}的[一-鿿]{2,5}",
    "Chained 的…的…的": r"的[^，。]{1,8}的[^，。]{1,8}的",
}

# Baseline: rules confirmed in research to discriminate; same script, same corpus
BASELINE = {
    "[baseline] ordinal paragraph opener": r"(?:^|\n)\s*(首先|其次|再次|最后|第一|第二|第三|一方面|另一方面)",
    "[baseline] 不是…而是 (not A but B)": r"(不是|并非)[^，。]{1,20}(，|)而是",
    "[baseline] Em dash": r"——",
    # Matches only cue phrase + colon; a wide regex (any Han char + colon) would also count headings, lists, dialogue
    "[baseline] Cue-phrase colon": (r"(?:一句话(?:总结|说|概括)|简单说|说白了|总结|小结|结论|核心(?:是|在于|观点)?"
                       r"|关键(?:是|在于)?|重点(?:是)?|原因(?:如下|有|在于)?|问题(?:是|在于)?"
                       r"|答案(?:是)?|本质(?:是|上)?|定义(?:是)?|具体(?:来说|如下|包括)?"
                       r"|举例(?:来说)?|换句话说|也就是说|我的(?:观点|判断|结论)|建议(?:是)?)[：:]"),
}


def model_of(path):
    return re.sub(r"-T\d.*", "", Path(path).stem)


def main():
    dirs = sys.argv[1:]
    if not dirs:
        print(__doc__)
        return
    files = [f for d in dirs for f in Path(d).rglob("*.md") if f.parent.name != "_meta"]
    if not files:
        print(f"No corpus found: {dirs}")
        return

    texts = {f: f.read_text(encoding="utf-8") for f in files}
    joined = "\n".join(texts.values())
    kchars = len(re.findall(r"[一-鿿]", joined)) / 1000
    models = sorted({model_of(f) for f in files})
    print(f"Corpus: {len(files)} docs, {kchars/10:.1f} 10k Han chars, {len(models)} models: {', '.join(models)}\n")

    # Han chars per model, for per-model rates
    mk = defaultdict(float)
    for f, t in texts.items():
        mk[model_of(f)] += len(re.findall(r"[一-鿿]", t)) / 1000

    rows = []
    for name, pat in {**MARKERS, **BASELINE}.items():
        rx = re.compile(pat)
        total = len(rx.findall(joined))
        docs = sum(1 for t in texts.values() if rx.search(t))
        per_model = {m: len(rx.findall("\n".join(t for f, t in texts.items() if model_of(f) == m))) / mk[m]
                     for m in models}
        rows.append((total / kchars, total, docs, name, per_model))
    rows.sort(reverse=True)

    head = f"{'Marker':<38}{'Per 1k':>8}{'Total':>7}{'Coverage':>10}  " + "".join(f"{m[:11]:>12}" for m in models)
    print(head)
    print("-" * len(head))
    for per_k, total, docs, name, pm in rows:
        cov = f"{docs}/{len(files)}"
        line = f"{name:<38}{per_k:>8.2f}{total:>7}{cov:>10}  " + "".join(f"{pm[m]:>12.2f}" for m in models)
        print(line)


if __name__ == "__main__":
    main()
