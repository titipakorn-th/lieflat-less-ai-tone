# Stage 1 | Detection and Suggestions (before revision)

Article: 《Agent 的记忆问题：为什么你的 AI 助手总在失忆》 (“Agent Memory: Why Your AI Assistant Keeps Forgetting”)

## Scope and criteria

The original is about 2,620 Han characters, with 46 body paragraphs detected. The script first counts fixed constructions, punctuation and structure, then extracts 85 semantic candidates, which the model classifies one by one against closed criteria: 33 synonym-renaming paragraphs, 36 cohesion links between paragraphs, 15 colon sentences, and 1 isomorphic triple.

Significance follows the skill's existing method. At the script layer: paired Wilcoxon test and Cliff's δ (the project threshold is |δ| ≥ 0.33). At the semantic layer: paired comparison of closed labels. "Significant" below refers to **human-vs-AI differences in the research corpus**. This report does not recompute significance for this article, and does not use it to judge whether the author is an AI. Whether a single article is worth editing also depends on where the hits fall and what they do.

## Metrics

| Metric and layer | Result in this article | Research baseline and significance | Judgment for this article |
|---|---|---|---|
| Contrast reversal (“不是 A 而是 B”, “not A but B”): script layer | 2 hits, 0.763 per 1k chars | Round one: humans ≈ 0.22, AI ≈ 0.73 per 1k chars. In the 270-pair matched retest, GPT and Opus were both significantly higher, same direction. Supported by both rounds. | Both are in the body argument; recommend editing. |
| Enumeration comma list ≥3 (dense three-item lists): script layer, model checks function | 10 raw hits, 3.817 per 1k chars. Of these, 6 in the body can be edited; 4 in the classification list should be kept. | Round one: humans ≈ 1.78 per 1k chars. In the paired retest, AI ≈ 1.45× humans; significant, same direction. The paired round and script counts use different bases, so the ratio cannot be applied to compute how far this article exceeds the baseline. | Edit only the 6 body hits; do not change the list just to reach zero. |
| Conclusion-cue colon: semantic layer | Of 15 colon candidates, 4 judged “conclusion cue”. The rest: 3 headings, 2 quotations, 6 other body colons. | In the paired retest this category differs significantly, AI ≈ 2.1–2.2× humans. **The total number of colons is not itself the signal.** | Edit these 4; keep the other colons. |
| Isomorphic triple: semantic layer | Coarse screen: 1 group, judged “highly isomorphic”. | Paired retest: this category differs significantly, AI 29.4%, human 10.7%. For single-article flagging, this skill's threshold is at least 2 groups. | Only 1 group here, so not a strong judgment. One low-risk syntactic tweak is possible. |

## Hit examples and planned edits

**1. Contrast reversal.** Line 13, “不是冰箱的容量，而是……” (“it is not the fridge's capacity but…”), and line 76, “不是存更多，而是分清楚” (“not storing more but distinguishing clearly”), both put the negated side first and then the real claim. The construction appears twice, and both carry a paragraph's conclusion, so the repetition is more noticeable than a single instance. Planned edit: state the judgment directly while keeping the negated information. Fridge capacity cannot decide whether you can find the shrimp; beyond storage size, a memory system must distinguish recency, certainty and credibility. Do not simply delete “容量” or “存储量” (capacity or storage volume), so the argument does not change.

**2. Dense three-item lists.** Line 15, “对的内容、以对的形式、以对的顺序” (“the right content, in the right form, in the right order”), and line 25, “搜什么、搜几次、用不用搜到的内容” (“what to search, how many times, whether to use what is found”), are representative. All three items carry information; the problem is similar structures running in a row. Planned edit: rewrite the first as “把对的内容，按合适的形式和顺序送进 LLM” (“send the right content to the LLM in a suitable form and order”). For the second, keep the three conditions but fold them into one complete action. Lines 67–70 (four hits) are in the file-classification list, where full enumeration is the point; keep them.

**3. Conclusion-cue colon.** Line 31, “技术层面的原因其实不复杂：每次开新对话……” (“the technical reason is actually simple: every new session…”), and line 49, “核心记忆解决的是完全不同的一个问题：……” (“core memory solves a completely different problem: …”), both use an abstract claim to signal “the key point follows” before the concrete content. The other two are at lines 7 and 76. Planned edit: check each front clause. If it carries information, keep it and end the sentence with a period; delete only pure signposts. The title colon, the colon introducing Naomi's quote and the colon before the list are not in this category; keep them.

**4. One set of isomorphic triples.** Line 45 reads “短期记忆像……；核心记忆像……；档案记忆像……” (“short-term memory is like…; core memory is like…; archival memory is like…”). The three metaphors explain three different recall timings, and the content is useful; only the skeleton is fully parallel. Since this is the only group detected in the article, it is not a strong signal on its own. For a low-risk tweak, change the word order of one clause only, and keep the three images: sticky note, ID card and filing cabinet.

## Not in revision scope

Synonym renaming (semantic layer) found 1 group across the 33 candidate paragraphs; there is no concentrated “same concept renamed in every paragraph” problem. The longest continuous explicit carry-over between paragraphs is 5 links, below this skill's threshold of ≥6. The script's flag on line 3, “long pre-modifier”, is a false positive on review. Em dash density is 3.053 per 1k chars, but the dashes mainly separate definitions and list items for the three memory layers and four file types. This metric also shows a clear model difference, so do not remove them uniformly by count. Subheading numbers, “这意味着什么” (“what does this mean”), questions, quotations and metaphors are not cleaned up just because detection flagged them.

## Recommendation and pending confirmation

Recommended scope: edit the two contrast reversals, the six body dense lists and the four conclusion-cue colons, and make one light adjustment to the three-clause skeleton at line 45. Keep facts, numbers, qualifiers, quotations, metaphors, lists, sections and paragraph order. Retest with the same script, then deliver the revised full text and the side-by-side page.

If you approve this scope, reply `按建议改` (“apply the suggestions”). To keep a certain pattern type, name that type. No body text changes until a reply arrives.

Detection data: [Script results](data-detect-before.json) · [Per-item semantic labels](data-semantic-labels.json).
