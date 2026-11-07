"""Smoke test for detect.py patterns: python3 scripts/test_detect.py"""
import re
from detect import REGEX_HITS, CHAR_HITS, measure_docs, extract_candidates

PAT = {name: pat for _, name, pat, *_ in REGEX_HITS + CHAR_HITS}

CASES = {
    "Contrast reversal": (["The real barrier isn't technology, it's cognition.",
                           "The problem is not capacity but placement.",
                           "It's less about storing more than about sorting well.",
                           "What decides it is not the fridge's capacity. It is which shelf you use."],
                          ["I'm not only tired but also hungry.", "This is a plain sentence."]),
    "Cue-phrase colon": (["In short: the plan costs too much.", "The key is: speed.",
                          "The technical reason is actually simple: no state.", "This is a deeper problem: teams forget."],
                         ["She said: hello.", "Time: 9am", "See the docs at https://x.io"]),
    "Opening formula": (["To put it bluntly, nobody reads the docs.", "Here's the thing — it works."],
                        ["He put it bluntly to me."]),
    "Topic-shell frame": (["When it comes to hiring, early teams struggle."], ["They came to hire."]),
    "Sentence-initial connective": (["However, the test failed.", "It ran. Moreover, it passed."],
                                    ["The test, however, failed."]),
    "Serial list ≥3": (["We need speed, accuracy, and cost control."], ["We need speed and accuracy."]),
    "Personifying metaphor": (["It works like a tireless junior reviewer."], ["The reviewer approved it."]),
    "Ordinal subheading (rejected)": (["## 1. Setup", "### First steps"], ["## Setup"]),
    '"This means" restatement (rejected)': (["This means the cache is cold."], ["The cache is cold."]),
    "Em dash": (["The answer is simple — focus."], ["The answer is focus."]),
}

for name, (pos, neg) in CASES.items():
    for s in pos:
        assert re.search(PAT[name], s), f"{name} missed: {s}"
    for s in neg:
        assert not re.search(PAT[name], s), f"{name} false positive: {s}"

doc = ("However, the model forgot everything. " * 3 + "\n\n") * 4 + \
      "The key is: memory is about retrieval, not storage. We use, utilize, and leverage tools.\n" * 20
r = measure_docs([("t.md", doc)])
assert r["meta"]["words"] > 300 and r["hits"]["Sentence-initial connective"]
assert r["syn_hits"] and r["structure"]["Sentence-length CV"] is not None
c = extract_candidates([("t.md", doc)])
assert c["colon"] and c["cohesion"]
print("ok")
