---
layout: post
category: Evals
tags: [LLM evals, TypeSafe, Jev, Claude, cost]
description: "Notes from testing TypeSafe's Jev as a replacement for a Claude-based answer grader. It matched Claude without source text, did worse with it, and its confidence score turned out to be the useful part."
title: "Evaluating Jev as a Replacement for an LLM Answer Grader"
---

Setup: we train small language models on collections of documents, then check how well each one learned the material by asking it a few thousand questions and having a large commercial model (Claude) grade the answers against a rubric. The grading step costs about ~$100 per run in API spend. For scale, an hour on an 8-GPU machine costs $29.40, so grading is roughly 3.5 hours of GPU cost per run, spent deciding whether the GPU time was worth it.

<!--more-->

TypeSafe recently released Jev, and I spent a few days testing it as a replacement for that grader. This post is the writeup. The short version: it matches Claude on grading accuracy when neither is shown the source document, falls behind when both are, and returns a confidence score that is reliable enough to make decisions on. Used as a first-pass filter in front of Claude rather than a replacement, it cuts the grading bill by about 78% at the cost of half a percentage point of accuracy.

## What Jev is

Jev does not generate text. It is a model that answers structured questions about an input. You send it a chunk of data and a list of questions with fixed answer types, and it returns answers in those types. The question types are `Choice` (pick one of N options; returns the option, a probability for each option, and an overall confidence score), `Score` (a number against a rubric), and `Noul` (yes/no). Because nothing is generated, you only pay for input: $0.042 per million input tokens. Median response time on my calls was about 400ms.

This matters because our grader is already, functionally, a `Choice` question. We prompt Claude for `{"verdict": "correct" | "incorrect" | "partial", "confidence": 0.0-1.0, "reasoning": "..."}` and parse the result. Around that we have retry logic and a function that recovers a verdict from cut-off JSON. That function exists because one run had 472 of 6,657 verdicts get truncated at the output length limit and default to `incorrect`, which silently invalidated the run. None of that code is about grading. It is the cost of asking a text generator for a structured decision.

## Method

I ported our four grading rubrics to Jev. Each rubric's CORRECT/INCORRECT/PARTIAL criteria became the three options of a single `Choice` question. I then ran both graders against 100 cases that a person had already graded by hand, two passes each, for 200 judgments per grader. The metric throughout is how often the grader agrees with the human.

Two conditions: with and without the source document. Our production grader gets a ~10,600-character window of the original document around the fact being tested. We added that the week before this test; it moved Claude from 89.0% to 93.0%, mostly by catching wrong answers it had previously marked correct.

## Results: grading accuracy

Without the source document:

| Grader | Source evidence | Human-label agreement |
|---|---|---:|
| Claude Opus 5 | none | 89.0% |
| Jev | none | 89.0% |

Identical, and not just in total: the same 178 of 200 judgments are correct. The two graders agree with each other on 92 of 100 cases, are both wrong on 7, and each is uniquely right on 4. Across roughly 4,800 Jev calls total there were zero parse failures and zero truncated outputs.

With the source document:

| Grader | Source evidence | Human-label agreement |
|---|---|---:|
| Claude Opus 5 | 10,600-char window | 93.0% |
| Jev | 10,600-char window | 88.5% |

Jev gets slightly worse when shown the source. TypeSafe's docs describe this failure mode directly ("large state full of irrelevant detail — filter first; send only what the question needs"). The windows are three neighboring document chunks picked by position, so most of the text has nothing to do with the question.

## Trimming the source text did not fix it

If the problem is too much irrelevant text, the obvious fix is to shrink the window. I wrote four filters and cut the windows to 7.5–10.9% of their original length:

1. Keep the sentences that share the most words with the question. No model involved.
2. Ask Gemini Flash to extract the relevant sentences, two prompt variants.
3. Ask Jev a yes/no `Noul` question ("is this sentence relevant?") about every sentence at once, in a single call.

Before running anything I wrote down 91.0% as the bar for "partially fixed." The best filter came in at 90.5%, and all four were too close to each other to tell apart. So: no.

Looking at why was more useful than the result. One case in the set had been flagged by our human reviewer as the key example: the model's answer applied a rule from paragraph b(6) when the question asked about b(5). All four filters kept both paragraphs. The most aggressive one reduced 74 sentences to four (981 characters), and those four were, consecutively and word for word:

```text
(5) The appropriate qualification standard and any selective certification or
quality ranking factors which may be appropriate;
(6) The appropriate recruitment sources and techniques to use and whether to
use them singularly or in combination.
```

Jev marked the answer correct with all four filters, both passes. Across the failed cases where the reviewer left a note, the filtered windows kept 87.5% of the specific terms the reviewer pointed to in the source, which is higher than the filters' average. The relevant text was there.

So this is not a problem of too much irrelevant text. Rejecting that answer requires noticing that the rule came from the paragraph next door, not the one the question asked about. That is a reasoning step Jev does not appear to take. It handles "does the source support this claim" reasonably well; it does not handle "this claim is supported by the wrong part of the source."

## A mistake I almost made

The two graders disagreed on 290 judgments. To break the ties I sent those rows to Claude Opus 5 as a tiebreaker, without telling it which grader said what, using our own grading prompts. Then I repeated it with a model from a different vendor.

| Tiebreaker | Sides with Jev | Sides with Claude grader |
|---|---:|---:|
| Claude Opus 5 | 73 | 155 |
| Gemini 3.8 Flash | 137 | 100 |

The result flips depending on which tiebreaker you ask. Both pass the same sanity check: on rows where the two graders already agreed, they side with the agreed verdict 95.8% and 91.7% of the time respectively. But our grader is Claude, and using Claude to judge Claude roughly doubled its apparent advantage. Counting only the rows where both tiebreakers agree gives 79 to 58 in Claude's favor: a real edge, but less than half of what the first number suggested.

If you are using an LLM to settle disagreements between graders, use one from a different vendor than any grader being tested, or use two and only count the rows where they agree.

## Is the confidence score any good?

Every Jev response includes a confidence score. It is computed from the probabilities Jev assigns to each option, not written out as text by the model. I had been ignoring it because I was evaluating verdicts.

Grouping judgments by the confidence the grader reported:

| Reported confidence | Jev rows | Jev agreement | Claude rows | Claude agreement |
|---|---:|---:|---:|---:|
| 0.2–0.3 | 59 | 37.3% | — | — |
| 0.5–0.6 | 91 | 58.2% | 11 | 54.5% |
| 0.6–0.7 | 113 | 64.6% | 25 | 12.0% |
| 0.7–0.8 | 131 | 74.8% | 149 | 25.5% |
| 0.9–1.0 | 1,587 | 97.9% | 1,833 | 97.1% |

Jev's accuracy rises steadily with its reported confidence across the whole range: when it says it is unsure, it is usually wrong, and when it says it is sure, it is usually right. Claude's self-reported `confidence` field does not behave this way. It never reports a value below 0.5, it puts 79% of rows at 0.9 or above, and it is less accurate in the 0.6–0.7 bucket than in the 0.5–0.6 bucket. We use a threshold of `min_judge_confidence = 0.70` to decide which judgments a human should look at. On Claude's self-report that threshold flags 1.6% of rows for review. On Jev's it flags 18.9%, and those rows really are the disputed ones.

## Jev as a first-pass filter

Given a confidence score you can trust, the natural setup is two stages: accept Jev's verdict where it is confident, and send the rest to Claude.

| Configuration | Jev serves | Human-label | Cost/run |
|---|---:|---:|---:|
| Current: Claude + full window | — | 93.0% | $109 |
| Claude + question-conditioned window | — | 92.5% | $71 |
| Jev → Claude + full window | 57.0% | 92.5% | $47 |
| Jev + Claude, one shared window | 66.5% | 92.5% | $24 |

0.5 points is one judgment in 200. Cost drops by about 78%.

This works because the confidence threshold picks out exactly the rows where Jev is not worse. On the two thirds of rows Jev is confident about, Jev and Claude both score 95.5%, and they mark the same six wrong answers as correct. On the third Jev flags as uncertain, it trails Claude by 7.5 points. Splitting the rows randomly at the same ratio would not work, since Jev on its own is 3–4 points behind overall.

The second row is worth noting on its own because it requires no new vendor. Cutting the source window down to roughly 900 characters costs Claude nothing in accuracy (92.5% either way) and halves the input tokens, as long as the filter is based on the question rather than on the answer being graded. Since both the question and the document are fixed, the filtered window can be computed once per question set and cached.

## Caveats

- I picked the confidence threshold after the fact, on the same 100 cases I used to measure Jev's confidence in the first place. That is circular. The overall shape (higher confidence, higher accuracy) is probably real; the specific threshold and the 92.5% figure are not validated.
- The test set is straightforward fact-recall questions only. Jev's grading agreement was weakest on trick questions designed to catch the model out, which is exactly where marking a wrong answer correct does the most damage.
- Only 100 cases. The differences between the four filters, and between Jev and Claude when neither sees the source, are too small to be meaningful.
- This saves money; it does not improve accuracy. If you could somehow pick the better grader for each case, you would score 94.0–94.5%. The two-stage setup captures none of that.

A proper test would fix the threshold on one set of cases and then score it on a fresh, human-graded set covering every question type.

## Summary

- Jev matches Claude on grading accuracy without the source document (89.0% both) and falls behind with it (88.5% vs 93.0%).
- The gap is not fixable by filtering the source text. It comes from a reasoning step (noticing a claim is backed by the wrong passage) that the model does not perform.
- Settling grader disagreements with a model from the same vendor as one of the graders roughly doubles that grader's apparent advantage.
- Jev's confidence score means what it says; our Claude grader's self-reported confidence does not, and tells you almost nothing below 0.9.
- Using Jev's confidence to decide which cases go to Claude keeps accuracy within 0.5 points and cuts grading cost by ~78%, subject to the caveats above.

If you are evaluating a model like this, measure the confidence score, not just the verdict. In our case the verdict was a tie and the confidence was the result.
