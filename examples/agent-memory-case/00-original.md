Agent Memory: Why Your AI Assistant Keeps Forgetting

A Japanese musician spent 10 hours pouring out all of her plans to an AI, and paid $30 for the service the next day. Nine minutes after paying, she discovered the AI had forgotten everything.

Her last words were: "In the end, nothing accumulates."

This is not an isolated case. Nearly every team building agent products faces the same awkward fact: users trust the AI as a partner, but its memory is worse than a goldfish's. At least a goldfish never promised the user "I'll remember."

The industry has a buzzword for this: "Agent Memory." LangChain is building OpenWiki Brains, OriginTrail is building shared memory systems for agents, and nearly every AI company claims it has "solved the memory problem." But look closer and you will find that most of these solutions are solving the wrong problem.

01 The Misnamed Problem

Imagine your brain is a refrigerator. The things you bring home from the supermarket (the information gained in a new conversation) do need somewhere to go. But what decides whether you can find that bag of shrimp when you cook tomorrow is not the refrigerator's capacity. It is which shelf you put it on, whether you labeled it, and where your eyes go first when you open the door.

The name "Agent Memory" draws everyone's attention to "how to store it," but what really determines the outcome is whether, when answering a specific question, the system can send the right content to the LLM, in the right form and the right order.

An R&D team ran a systematic evaluation, comparing memory approaches from six major schools on the market. The result is somewhat counterintuitive.

Under identical test conditions, the simplest approach (keep the raw conversation text and search it by keyword) scored higher than most carefully engineered systems. BM25, a text retrieval algorithm born decades ago, ranked consistently near the top across three rounds of evaluation.

What does this mean? The approaches that invest heavily in "memory distillation" (using an LLM to compress conversations into fact cards, then storing them in a vector database) actually lose key details during compression. The tone and context of what the user said, along with their conditions and qualifiers, are gone after compression. When the information is needed, the retrieval system gets a pile of dry conclusions, stripped of their original warmth and precision.

The evaluation data is clear. Approaches that keep the original text (MemMachine, 0.9169) significantly outperform the fact-extraction school (Mem0, about 0.68). A one-time LLM extraction is a clearly negative-ROI move.

This conclusion has one important boundary condition. If, at read time, the agent decides for itself what to search for, how many times to search, and whether to use what it finds (similar to Letta's approach), the losses from compression can be recovered. But if the content is compressed and stored, waiting to be hit by passive retrieval, a miss is a miss.

So the real question is not "how do we make AI remember more." The question is "how do we deliver the right information to the AI at the right moment." Storing is only the first step. Retrieval is what matters.

02 Three Layers of Memory: From Forgetting to Knowing What to Remember

Back to Naomi's story. Why did her AI assistant forget everything overnight? The technical reason is actually simple: every time a new conversation (session) starts, the AI sees a blank page. The context of the previous conversation is gone, and no mechanism carries yesterday's key information into today.

What does this resemble? A company with no handover process. Your colleague spent three hours with a client yesterday, and today you take over, but he left nothing behind. When the client calls, all you can say is, "Hello, may I ask who is calling?"

The current approach solves this in three layers:

Short-term memory — a summary of task status from the last 7 days, refreshed every hour. It answers "what have I been busy with lately?"

Core memory — preferences and agreements that stay stable across conversations, injected unconditionally at the start of every conversation. It is "what you should know without my having to ask." For example, the user's preferred communication style, the team's tech stack, and a few hard lines that must never be crossed.

Archival memory — vector retrieval over the full history of conversations, queried actively when needed. It is "everything we have discussed before."

Why three layers instead of one big layer?

Because the three layers correspond to three completely different moments of use. Short-term memory is a sticky note on your desk: you see it the moment you look up. Core memory is your ID card: you carry it everywhere. Archival memory is the company filing cabinet: you open it only when you know what you are looking for.

Schemes that put all memory into one layer do exist. In tests they also scored highest (in the LoCoMo evaluation, the generic-roster scheme ranked first with a 79% pass rate). But the cost is more than 10,000 tokens of context consumed in every conversation. For free users, lightweight conversations, and scenarios that need fast responses, that cost is completely unacceptable.

Core memory is the most subtle layer in the entire design. Existing benchmarks all test "the user asks a question, and can the system find the answer in its history?" Core memory solves a different problem: "What should the agent know even when the user asks nothing?" No existing evaluation can measure this dimension.

Naomi's expectations were actually simple: I told you my monthly income target is ¥400,000–500,000 (it must be hit). I was burned by a previous AI, so I have zero tolerance for forgetting. I do not want you to post on social media automatically. I should not have to say these things every time. You should just remember them.

If these three points had been automatically injected when she opened a new conversation the next day, her trust would not have collapsed.

03 Organizational Memory: Not Just an Individual Agent's Business

So far we have discussed the memory of a single agent. But in a team setting, the problem escalates by one dimension.

A PM spent two weeks discussing product direction with an AI, forming a series of judgments and decisions. Some of these judgments have been signed off; others are still just personal thinking. A new R&D colleague asks the AI: "Why are we building this feature this way?" Which version should the AI cite?

If it cites a draft still under discussion and presents it to R&D as settled, what happens? Misleading. If it cites a consensus that has been signed off but does not say where it came from, and R&D asks for the basis, the AI cannot explain. What happens then? Distrust.

This is a deeper problem: a team's knowledge also needs "memory levels."

Internally, we sorted every file in the team space into four tiers by credibility:

- Raw materials — verbatim user interview quotes, data screenshots, original external articles. First-hand facts, not changed or deleted; when an agent cites them, it may only restate them as facts, not interpret them.
- Analysis inputs (compiled) — analysis, research, and thinking based on raw materials. Grounded, but not yet signed off. When an agent cites them, it must state that "this is someone's analysis from a given date, not team consensus."
- Team consensus (canon) — decisions confirmed through a formal sign-off process. An agent can cite them directly as "current truth" without any prefix.
- Work in progress (workspace) — PRD drafts, meeting notes, RFCs. They will "graduate" (ship, get finalized, get archived), but until then, the agent must mark them as "in flux, not finalized."

Why do this? Because an agent is not like a person. A person reading a draft naturally knows "this isn't settled yet," but an AI reads text and treats it as fact. Back to Naomi's story: her AI read a draft of the weekly meeting prep, cited the numbers in it as confirmed analysis conclusions, and the user immediately identified it as a "hallucination."

Encoding credibility directly into the directory location means an agent knows whether it can treat a file as truth just by seeing which tier it sits in. This is admittedly a crude method. But while AI cannot yet judge the reliability of information on its own, a crude method is the only reliable one.

This tiering and the three layers of personal memory follow the same idea. It is not about storing more; it is about separating things clearly. Separate timeliness (short-term vs. long-term), certainty (core memory vs. history awaiting retrieval), and credibility (signed-off consensus vs. personal analysis).

04 Problems Still Unsolved

Having said all this, there are several things we must candidly admit we have not solved well.

Timing of session closure. When a conversation ends, key information should automatically be distilled and written into long-term memory. But "the conversation has ended" is itself a vague concept. Users may come back at any time. Trigger too early and information is lost; trigger too late and it is as if it never triggered.

Write standards for core memory. What counts as a "stable preference"? If the user says "I like concise answers" once, does that count? Three times? What if she changes her mind next week? Implicit preferences (every time she gets a long answer, she says "shorter") are harder to catch, because there is no explicit statement for vector retrieval to hit.

The eternal tension between write cost and retrieval quality. The evaluation data reveals an industry-wide pattern: the more rigorous the write process (multiple LLM analyses, building knowledge graphs), the more likely it is to collapse as the data grows. Four complex schemes all failed outright in long-conversation tests because writes timed out. There is no approach that delivers cheap writes, rigorous updates, and zero LLM cost at retrieval all at once.

Memory sharing across agents. A team has multiple AI roles. The customer-service agent knows the user got angry. Does the product agent need to know? How much should be shared? Today, there is no good answer to this question.

Finally

Memory is the least glamorous infrastructure in agent products. No one posts on social media that "your AI remembered what I said last week." But it determines something fundamental: whether trust can truly accumulate between AI and people.

The Japanese musician's last words, "nothing accumulates," are an indictment of the entire agent industry. If AI has no reliable memory, it can only be a stranger who has to reintroduce itself every time you meet. No matter how strong its reasoning or how fast its tool calls, trust simply cannot build up.

The industry is shifting from "what agents can do" to "what agents can remember." This shift has none of the excitement of a GPT-5 launch, but it may shape the actual product experience more than any model update.
