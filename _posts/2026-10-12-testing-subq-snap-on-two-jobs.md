---
layout: post
category: Evals
tags: [LLM evals, SubQ, Snap, JevK5, tool selection, answer grading, decision models]
description: "SubQ Snap, a hosted decision model, got every tool choice right on a 250-case tool-selection test and cost a fraction of a cent. On the same 100 hand-graded answers we use for every grader, it agreed with the human labels 84% and 86% of the time, behind JevK5-4B's 90% and 88%."
title: "Testing SubQ Snap on Two Jobs: Picking Tools and Grading Answers"
---

[SubQ Snap](https://docs.subq.ai/) is a hosted decision model: you send it some context, instructions, and a fixed set of options, and it returns one option plus a probability for each. No prose, nothing to parse. That is the same shape as Jev, the open JevK5 models, and OpenAI's Decisions API, all of which I have tested here as answer graders. I ran Snap through two jobs: having an agent pick the right tool for a request, and grading a model's answer against a known fact. It did very well at one and not the other.

<!--more-->

Short answer: it was the best tool picker we have measured, and a middling answer grader. Every tool decision in a 250-case test came back right, with a median response time of 155 ms and a total cost under a cent. On the 100 hand-graded answers, it agreed with the human labels 84% of the time without the source document and 86% with it. JevK5-4B, our preferred local grader, scored 90% and 88% on the exact same requests. The rest of this post is about why I think both of those things are true at once, and what I am actually going to do with them.

A note on how the tests were run, since it matters for what follows. Nothing was changed for Snap. We kept the datasets and request formats from earlier runs, added Snap as one more model, and read every competitor's number from its saved, audited record. No prompt edits after seeing scores, no retries to nudge a result. Both experiments passed independent audits.

## The tool-picking test

The dataset is the public [BFCL V4 Live routing adaptation](https://huggingface.co/datasets/pyuvraj/bfcl-v4-jev-routing/tree/9cd92d8c7789eb390d271adbd7312bbb3e3657cf). It has 250 requests. In 150 of them the model sees several tools and one is the right one; in fifty it sees exactly one tool, and that tool applies; in the last fifty no offered tool applies at all. For each request the model gets the user's message and the tool descriptions and picks from four to seven options, three of which are non-tool actions: say no tool is needed, ask a clarifying question, or say it cannot help.

Here are the rows that matter from a fourteen-model comparison:

| Model | Agreement | Unnecessary tool calls (of 50) | Median response time |
|---|---:|---:|---:|
| SubQ Snap Preview | 100.0% | 0 | 155 ms |
| JevK5-9B | 98.8% | 3 | 239 ms |
| Tura-S1-4B | 98.4% | 4 | 373 ms |
| JevK5-4B MLX | 97.6% | 2 | 168 ms |
| OpenAI Decisions, gpt-6-luna | 94.8% | 0 | 162 ms |
| Jeff 0.8B | 94.8% | 1 | 51 ms |

Snap picked the right tool on all 200 cases where a tool applied, and never reached for a tool on the fifty where none did. That is what the 100% means, and it is worth being precise about, because there is a looser and a stricter way to read those fifty negative cases.

The dataset accepts any of `no_tool`, `clarify`, or `cannot_answer` on a negative case. Snap chose `no_tool`, the canonical label, on 27 of them and one of the other two permitted actions on 23. If you insist on the canonical label, Snap's agreement drops to 90.8%, and Tura edges it at 92.0%. So "perfect" here means it never called a tool it should not have and never missed one it should have. It does not mean it always chose the best way to say no. If your product cares whether the agent asks a follow-up question versus answering directly versus declining, that is a separate test and this one does not cover it.

The margins are also smaller than the table makes them look. Snap beat JevK5-4B MLX by six judgments, Tura by four, and the 9B by three. Against the 4B that is +2.4 percentage points with a paired 95% interval of +0.8 to +4.4; against the 9B the interval includes zero. These intervals are descriptive and not adjusted for the fact that I am making several comparisons at once. The catalogues are small and public, so I cannot rule out training overlap, and the test says nothing about filling in tool arguments, executing the call, large tool inventories, or finishing an actual multi-step task. Still: every applicable tool, zero wrong calls, 155 ms, fractions of a cent. That earned a second test.

## The grading test

Human100 is the set I keep coming back to. It is 100 cases from one document corpus, each with a question, a reference fact, a candidate answer, the entities that have to appear, and a rubric. A person graded each one: 67 accepted, 33 rejected. The judge returns `correct`, `incorrect`, or `partial`; only `correct` counts as accepting the answer. We run two versions of each case, one with just the fact and rubric and one that also includes the original source text, and we run each version twice to check that the model is stable. For Snap that was 400 judgments. The repeats stay clustered by case in the statistics; they do not turn 100 cases into 400.

| Model | Without source | With source | Median response time (without / with) |
|---|---:|---:|---:|
| Jev | 90.0% | 88.5% | 438 / 461 ms |
| JevK5-4B MLX | 90.0% | 88.0% | 176 / 923 ms |
| JevK5-4B Q8 | 89.0% | 88.0% | 162 / 998 ms |
| Decider-4B v2.1 | 87.0% | 88.0% | 167 / 1,212 ms |
| SubQ Snap Preview | 84.0% | 86.0% | 154 / 211 ms |
| OpenAI Decisions, gpt-6-luna | 83.0% | 82.0% | 135 / 136 ms |

Snap marked eight of the 33 human-rejected answers as correct in both versions. It marked eight of the 67 human-approved answers wrong without the source text and six with it. Both repeat passes returned identical verdicts on every case.

The error pattern is more interesting than the totals. Without the source text, Snap and JevK5-4B MLX let through the same number of bad answers. The whole six-point gap comes from Snap rejecting good ones: eight distinct cases versus two. With the source text, Snap let through one fewer bad answer than MLX and rejected three more good ones. Those two kinds of mistakes cost different things in a real pipeline, and a single agreement percentage hides which one you are buying.

I would not read the gap as a ranking, either. Snap minus MLX is −6 points without the source, with a 95% interval of −12 to 0, and −2 points with it, with an interval of −9 to +5. On a reused set of 100 cases that is "probably a bit worse, maybe not". It is also not a reason to switch, which is the question I actually had.

## Why the same model would be great at one and ordinary at the other

My working guess is that these two jobs reward different kinds of judgment, and the shared interface disguises that.

Picking a tool from a small catalogue is mostly matching: does this request line up with one of these capabilities, or with none of them? Grading an answer is checking whether specific facts, entities, and conditions survived intact, and deciding whether what got dropped was important enough to fail the answer.

A toy version: deciding that a request should go to the returns-policy lookup tool is easy. Grading the answer that comes back means noticing that "30 days after purchase" is not the same as the reference policy's "30 days after delivery". The answer is relevant, fluent, on topic, and wrong. A typed-choice API does not do that noticing for the model; the model still has to.

I want to be clear that this is a hypothesis. We did not isolate anything about Snap's architecture or training data, the two datasets differ in domain and in how they are scored, and tool selection presumably gets much harder as catalogues grow and tools start to overlap. The honest version of the claim is: on these two tests, the ordering flipped, and I have a plausible story for why.

## Speed and money

Even where Snap lost on accuracy, it was quick. With the source text included, its median response time was 211 ms against 923 ms for the JevK5-4B MLX recipe we measured, about 4.37 times faster. Those requests ran roughly 2,300 to 4,300 input tokens, which is real document handling but well short of the long context SubQ advertises. The local timings were on an M5 Max with 128 GB of memory, in different sessions from the hosted ones, so this compares two practical setups rather than isolating anything about the model, and it says nothing about throughput under load.

At SubQ's [published pricing](https://subq.ai/) of $0.05 per million input tokens with free output, the entire tool-picking experiment including controls cost an estimated $0.002835. Human100 including controls was $0.032868. Both together: about 3.6 cents. I like that number mostly because it means trying a new model on our full test set is now a rounding error, whether or not the model wins.

One thing that did not pan out was using Snap's probabilities as a filter. We have a standing rule from earlier posts: if a grader's top probability clears 0.95, let the verdict stand, otherwise hand the case to a larger model. That screen kept only 21% of the cases without the source text and 12% with it. The 21% still included a wrong answer marked correct. The 12% was error-free but amounted to twelve unique cases, which is nowhere near enough to certify a production cutoff. We did not fit a new threshold and nothing in production changed.

## Where this leaves things

For the next round of agent tool-selection work, Snap goes in as the hosted model to beat. For grading answers against documents, I am starting with JevK5-4B MLX, same as before, and nothing here moved me off it. Fresh cases, more domains, and an honest accounting of what each kind of error costs in our pipeline will decide what happens after that.

The general point is that a shared interface does not make the tasks behind it interchangeable. Snap, JevK5, and the OpenAI endpoint all take the same kind of request and return the same kind of answer, and the ordering between them still flipped from one job to the other. A result on one of these tasks says little about the other; each needs its own test.
