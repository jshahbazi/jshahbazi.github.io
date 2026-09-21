---
layout: post
category: Evals
tags: [LLM evals, TypeSafe, Jev, Claude, cost]
description: "I evaluated a text-free decision model as a replacement for our eval grader. It lost on the thing I was measuring and won on a number I hadn't thought to shop for, which turned out to be worth about $85 a run."
title: "The Number I Wasn't Shopping For"
---

We fine-tune small models on document collections, then run a few thousand questions through each checkpoint and have a frontier model grade the answers. That grading bill is about $109 a run. An 8×A100 hour costs $29.40, so the grader is roughly three and a half GPU-hours of spend to decide whether the GPU-hours were worth it.

<!--more-->

So when TypeSafe shipped Jev, I was really interested in seeing how it would perform as a replacement for our eval grader. Actually, let me admit first that I wasn't really sure what it actually did. Lots of headlines say, "Faster LLM! Lower latency! Cheaper!" but I wanted to understand the mechanics before I got too excited. Is it an LLM? No, yes, sorta? It's a model that makes decisions based on structured input rather than generating text (to be more precise, it's a non-autoregressive "System One" classification and decision model). You send it a blob of state and a set of typed questions, and it returns typed answers. No prose. A `Choice` question comes back as one of your options plus a probability for each and a confidence score. There is also `Score` for rubrics and `Noul` for yes/no. Input is $0.042 per million tokens and output tokens are free, because there are no output tokens. Median latency on my calls was about 400ms.

Our grader is, more or less, a `Choice` question that Jev can handle directly. We ask Claude for `{"verdict": "correct" | "incorrect" | "partial", "confidence": 0.0-1.0, "reasoning": "..."}` and then parse it back out. We have a function to salvage a verdict from truncated JSON, because one run had 472 of 6,657 verdicts come back cut off at the token limit and fail closed to `incorrect`, which quietly invalidated the whole instrument. None of that machinery has anything to do with grading. It exists because we asked a text generator for a structured decision. And up until a few days ago, it was the best option we had.

## It tied

I ported our four grading rubrics to Jev questions — the CORRECT/INCORRECT/PARTIAL clause lists became the three options of one `Choice` — and ran both graders against 100 cases we had previously graded by hand, two passes each.

| Grader | Source evidence | Human-label agreement |
|---|---|---:|
| Claude Opus 5 | none | 89.0% |
| Jev | none | **89.0%** |

Identical. Not close — the same 178 of 200 judgments. The two graders agree with each other on 92 of the 100 cases, are both wrong on 7, and each is uniquely right on 4. Across about 4,800 Jev calls I had zero parse failures and zero truncated verdicts, because there is nothing to truncate.

Then the catch.

The week before, we had improved the grader by also showing it the original source passage around the fact being tested. That moved Claude from 89.0% to 93.0%, mostly by catching answers it had been wrongly accepting. Jev cannot use it.

| Grader | Source evidence | Human-label agreement |
|---|---|---:|
| Claude Opus 5 | 10,600-char window | **93.0%** |
| Jev | 10,600-char window | 88.5% |

Hand Jev the evidence and it gets slightly worse. TypeSafe documents this shape of failure themselves, under "large state full of irrelevant detail — filter first; send only what the question needs." The windows are three whole document chunks picked by adjacency, so most of that text is genuinely irrelevant.

## The obvious fix didn't work

If the problem is dilution, trim the evidence. I wrote four condensers — plain token overlap with no model at all, two using a cheap Gemini Flash, and one using Jev's own `Noul` fan-out to score every sentence in a single call — and cut the windows to between 7.5% and 10.9% of their original length. I wrote the bars down before running anything: 91.0% to count as partial recovery.

Best Jev arm was 90.5%. All four landed inside each other's noise. Missed.

The diagnosis was more useful than the miss. One case in the set is the one our human reviewer had flagged as decisive: the answer borrowed a rule from the adjacent numbered provision, b(6), when the question was about b(5). Every condenser kept both. The tightest one cut 74 sentences down to four — 981 characters — and those four included, consecutively and verbatim:

```text
(5) The appropriate qualification standard and any selective certification or
quality ranking factors which may be appropriate;
(6) The appropriate recruitment sources and techniques to use and whether to
use them singularly or in combination.
```

Jev read that and accepted the answer, in all four arms and both passes. Across the failing cases that carry a reviewer note, the condensations retain 87.5% of the terms the reviewer brought in from the source — higher than their own average.

So it was never a noise problem. Catching that answer requires noticing it had borrowed from the paragraph next door. That is a reasoning step, and Jev does not take it. It is good at "does the source support this" and not at "wait, that came from somewhere else."

## I nearly got this wrong in a way worth mentioning

Where the two graders disagreed, I needed a tiebreaker, so I ran the 290 disagreements past Claude Opus 5 with our own prompts, blind.

| Arbiter | Sides with Jev | Sides with Claude grader |
|---|---:|---:|
| Claude Opus 5 | 73 | **155** |
| Gemini 3.8 Flash | **137** | 100 |

Two to one against Jev, then the reverse when I asked a model from a different family. Both arbiters pass the same sanity check — on rows where the two graders already agreed, they endorse the agreed verdict 95.8% and 91.7% of the time. Our grader is Claude, so adjudicating it with Claude roughly doubled its apparent edge. On the rows where both arbiters concur it is 79 to 58, a real advantage and less than half of what the first tiebreak reported.

## The number I wasn't shopping for

Every Jev answer arrives with a confidence score derived from the returned probability distribution, not written by the model. I had been ignoring it because I was shopping for verdicts.

| Reported confidence | Jev rows | Jev agreement | Claude rows | Claude agreement |
|---|---:|---:|---:|---:|
| 0.2–0.3 | 59 | 37.3% | — | — |
| 0.5–0.6 | 91 | 58.2% | 11 | 54.5% |
| 0.6–0.7 | 113 | 64.6% | 25 | 12.0% |
| 0.7–0.8 | 131 | 74.8% | 149 | 25.5% |
| 0.9–1.0 | 1,587 | **97.9%** | 1,833 | 97.1% |

Jev's confidence climbs monotonically with accuracy across the whole range. Our Claude grader's self-reported confidence does not: it never emits anything below 0.5, it puts 79% of rows at 0.9 or above, and it is *less* reliable at 0.6–0.7 than at 0.5–0.6. We gate our triage on `min_judge_confidence = 0.70`. On Claude's self-report that gate selects 1.6% of rows. On Jev's it selects 18.9%, and those rows really are the contested ones.

That suggests using Jev as a router rather than a replacement. Take its verdict where it is confident; escalate the rest.

| Configuration | Jev serves | Human-label | Cost/run |
|---|---:|---:|---:|
| Today: Claude + full window | — | 93.0% | $109 |
| Claude + question-conditioned window | — | 92.5% | $71 |
| Jev → Claude + full window | 57.0% | 92.5% | $47 |
| Jev + Claude, one shared window | **66.5%** | **92.5%** | **$24** |

Half a point is one judgment out of 200. The bill drops by about 78%.

It works because the confidence finds exactly the rows where Jev is not worse. On the two thirds it is confident about, Jev scores 95.5% and the Claude grader scores 95.5% — the same number, and the same six false accepts. On the third it flags, Jev is 7.5 points behind. Random routing would have failed; Jev's overall arm is three to four points back.

The other line in that table is free money with no new vendor. Filtering the source window down to about 900 characters costs Claude nothing at all if you condition the filter on the *question* rather than on the answer being graded — 92.5% either way, half the input tokens, and because both the question and the document are fixed artifacts you can build the filter output once per question set and reuse it forever.

## What I haven't shown

The threshold was read off after the fact, on the same 100 cases I used to characterize Jev's confidence in the first place. That is circular, and it means I can quote the shape but not the number. The set is recall questions only, and Jev's verdict agreement was weakest on adversarial probes — the category where a false accept does the most damage. A real test pre-registers the threshold on a held-out slice and scores it on a fresh, human-labelled set covering every question type.

It is also a cost lever and not an accuracy lever. An oracle picking the better of the two graders per case would score 94.0–94.5%. The cascade captures none of that headroom. It preserves the current number and removes most of the bill.

## Final thoughts

I spent most of this evaluation on the verdict, because the verdict is what a grader produces and replacing the grader was the idea I had walked in with. Jev lost on the verdict for a specific and legible reason, and that would have been the end of it.

The confidence score was sitting in every response the whole time. It is the thing a decision model can offer that a text generator structurally cannot: a number computed from a probability distribution rather than a number the model wrote about itself. Our Claude grader has been emitting a `confidence` field all along, and we gate real decisions on it, and it turns out to carry almost no information below 0.9.

If you are evaluating one of these models, grade the metadata too. The verdict is the part you were shopping for. It may not be the part worth buying.
