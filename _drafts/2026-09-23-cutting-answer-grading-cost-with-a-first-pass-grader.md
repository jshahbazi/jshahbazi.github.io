---
layout: post
category: Evals
tags: [LLM evals, TypeSafe, Jev, Claude, cost, two-stage grading]
description: "How we put a cheap first-pass grader in front of Claude Opus, cut answer-grading cost per eval from about $43.60 to about $11, and checked that the verdicts still agree with Opus about 99 times in 100."
title: "Cutting LLM Answer-Grading Cost by 75% With a Cheap First-Pass Grader"
---

![Two-stage grading flow: 2,352 answers per eval go to Jev first; verdicts with confidence at or above 0.95 stand and agree with Opus 99.1–99.8% of the time, the rest go to Claude Opus 5. Cost per eval falls from about $43.60 to about $11, a 75% saving.](/images/two-stage-grading-flow.png)

Setup: we train a small open model on a customer's own documents. Every training run is evaluated three times: after stage 1, after stage 2, and once more at the end. Each eval asks the trained model 2,350 test questions and has a large commercial model, Claude Opus 5 on Vertex AI, grade each answer against the known fact. For questions answerable from the documents, Opus also sees a window of the source text, and that window was worth about four points of accuracy against human labels in an earlier test. Three evals per run, times a few thousand graded answers each, adds up.

<!--more-->

This post is about how we cut the grading cost by about 75%, from roughly $43.60 to about $11 per eval, while the verdicts we keep still agree with Opus about 99 times in 100. Two things up front. This is the grading cost only; GPU training and the other model calls in the pipeline are unchanged. And the dollar figures are estimates from token prices, not billed amounts, because we do not yet record billed grader usage.

## Short version

We put TypeSafe's Jev in front of Opus as a first pass. Jev grades every answer and returns a probability for its choice. If that probability clears a cutoff, its verdict stands; otherwise the answer goes to Opus exactly as before. With a cutoff of 0.95, Jev handles 60–62% of source-document questions and 91–92% of the rest. On the rows it handles, it agrees with Opus 99.1–99.8% of the time, which is about as often as Opus agrees with itself. The first version of this saved 35%; the saving came from coverage, not from Jev's unit price.

## Where the money went

The eval we measured had 2,352 questions in six categories:

| Category | Count | What it tests |
|---|---:|---|
| Recall | 854 | Facts answerable from the documents |
| Trick variants, category A | 928 | Questions designed to catch the model out |
| Trick variants, category B | 344 | Same, a second category |
| Kept-out | 148 | Answers deliberately left out of training; the right response is to decline |
| Nearby out-of-scope | 50 | Questions close to, but outside, what the documents cover |
| Regression | 28 | General behaviour has not broken |

I will call the last five categories "non-recall" from here on.

An Opus recall verdict costs about $0.0265, because it also reads a source window of roughly 3,300 tokens. A non-recall verdict costs about $0.014, and about 72% of that is output: Opus writes back a structured verdict with scores and a short explanation, and output tokens are the expensive kind.

## What Jev is, and why it is not a replacement

Jev is TypeSafe's decision model. It writes no prose. You give it the allowed verdicts and it returns a choice plus a probability for each. Input costs $0.042 per million tokens and output is free, which works out to about $0.000033 per verdict, several hundred times cheaper than Opus.

I [tested Jev against Opus earlier](/evaluating-jev-as-an-eval-grader) on a 100-case set graded by hand. Without the source document, the two tied at 89.0% agreement with the human labels. But Jev cannot use the source document; give it the window and it gets worse. Swapping graders outright would have handed back the four points the source window bought us. So Jev is a first pass, not a replacement.

## What we built

The two-stage setup is a per-run option, off by default. Jev grades first. If the probability of its top choice clears the cutoff, its verdict stands. Otherwise the answer goes to Opus with the same request it would have received anyway.

Failure handling is strict. Jev timeouts, rate limits and server errors send the answer to Opus. Configuration errors, such as a bad key or an unknown model name, fail the eval before any Opus money is spent. A failed Jev call is never turned into a verdict.

We treat a different grader as a different measuring instrument, because it is one. Each grading mode has its own identity string naming both models and the cutoff. The eval job checks at startup that it built the same identity the orchestrator wrote, and refuses to start, before any GPU or grading spend, if they differ. Stability comparisons between runs never mix runs scored by different graders.

Finally, we copied the grading instructions byte for byte from the research harness that measured them rather than retyping them. All 2,352 request bodies are byte-identical to what was tested.

Version 1 covered recall questions only, with the cutoff at 0.90.

## Method

Every comparison is a paired eval: the same trained model and the same questions, with only the grader changing, joined question by question.

Two things about the measurement had to be settled first.

Generation at temperature 0 was not deterministic. Only about 80% of answers were byte-identical across two evals of the same model. If you compare verdicts on answers that differ, generation noise looks like grader disagreement. So all agreement figures below are on questions where both evals produced the identical answer.

Opus disagrees with itself. On the same inputs, Opus versus Opus agreed 98.7% of the time on hard recall rows and 99.6% on non-recall. Any gap between Jev and Opus has to be read against that floor.

On the disagreements we ran a standard paired significance test (exact McNemar) and split them two ways. "Lenient" means Jev said the answer was right and Opus said it was wrong. "Strict" is the reverse. Lenient errors are worse, because they flatter the model being evaluated.

For the check on a second trained model, we wrote down the pass bar before looking at the results:

- Non-recall agreement with Opus of at least 99.0%.
- Recall agreement of at least 98.7%, matching the Opus self-agreement floor.
- No category significantly lenient.
- At most one lenient error on kept-out questions.

## Results

| Comparison | Cutoff | Handled by Jev | Agreement with Opus | Lenient errors |
| --- | ---: | ---: | ---: | ---: |
| Recall, first model | 0.90 | 67.7% | 99.2% | 3 |
| Non-recall, first model, re-graded offline | 0.90 | 94% | 99.6% | 2 |
| Non-recall, first model, re-graded offline | 0.95 | 92% | 99.7% | 0 |
| Non-recall, second model | 0.95 | 91% | 99.7% | 0 |
| Recall, second model | 0.90 | 67.6% | 98.4% | 6 |
| Recall, both models, re-cut | 0.95 | 60–62% | 99.1% and 99.8% | 4 in total |

Agreement is measured on Jev-handled rows with identical answers.

### Recall only, first model

Jev handled 67.7% of recall verdicts. On those it agreed with Opus 99.2% of the time, with 3 lenient and 1 strict disagreement. The headline recall score moved −0.2 points (p=1.0, too close to tell apart). The saving was only about 35%. The limit was coverage, not price: 74% of the remaining cost was non-recall questions still sent to Opus every time.

### Non-recall, offline

Before touching the non-recall categories in a live eval, we had Jev re-grade the exact answers Opus had already graded. Without a cutoff, it was not safe. On kept-out questions Jev accepted 7 of 148 answers as proper declines that Opus said were not (p=0.016). That is the worst kind of error on the product's weakest skill, knowing when not to answer. It was also stricter than Opus on one of the trick-question categories (p=0.011).

With the cutoff at 0.90, Jev handled 94% with 99.6% agreement and 2 lenient errors. At 0.95 it handled 92% with 99.7% agreement and no lenient errors. We chose 0.95 for non-recall, knowing it was read off the same data it was tested on.

### Second model

Non-recall passed. Jev handled 91%, with 99.7% agreement on 1,071 comparable rows, 0 lenient and 3 strict. On kept-out questions, 0 lenient of 95.

Recall failed. At the 0.90 cutoff, agreement was 98.4% on 494 rows, with 6 lenient and 2 strict, under the 98.7% bar. The result was not significantly different from the first model, and the headline recall score moved only +0.1 points. But across both models Jev leaned lenient on recall, 9 lenient against 3 strict (p=0.15). That is the direction we care about.

We tightened the system, not the bar. We raised the recall cutoff to 0.95. Re-applying that cutoff to the recorded probabilities gives 99.1% and 99.8% agreement on the two models, with 4 lenient errors against 1 across both. A stricter cutoff can only send more answers to Opus, so it cannot do worse than the looser one. The price is a saving of 75% instead of 79%.

## What it costs now

| Setup | Grading cost per 2,352-question eval |
| --- | --- |
| All Opus | about $43.60 |
| Two-stage, recall cutoff 0.90 | about $9.34 (79% saving) |
| Two-stage, recall cutoff 0.95 (what we ship) | about $11 (75% saving) |

Both two-stage rows use a 0.95 cutoff for non-recall. Per training run, with three evals, that is roughly $130 down to $33.

## What the results mean

Coverage sets the saving, not unit price. Jev is several hundred times cheaper per verdict, and version 1 saved 35%. Every question that still goes to Opus costs what it always did. The gain came from safely extending the cheap path to more categories.

The confidence cutoff is what made non-recall safe. Without it, Jev accepted 7 kept-out answers it should not have. At 0.95 it accepted none, on both models. The probability Jev returns finds the rows where it is unsure, without being told what those rows look like.

Lenient and strict disagreements are not interchangeable. Two graders can disagree on 1% of rows in a harmless way or a harmful one. Only the split told us Jev leaned lenient on recall; the headline recall scores moved by −0.2 and +0.1 points and would not have.

The remaining points are method notes, stated as rules we would reuse:

- Compare identical outputs only. Temperature 0 gave us byte-identical answers about 80% of the time; the other 20% is generation noise that would have been counted as grader disagreement.
- Read disagreement against the grader's own noise. Opus agrees with itself 98.7% to 99.6% of the time; a 99.2% Jev-to-Opus figure sits inside that.
- Fix the pass bar before you look. When you miss it, tighten the system, not the bar. We gave up four points of saving and kept the meaning of the metric.
- Label a new grader as a new instrument and never compare across the line. A cheaper grader that quietly inherited the old grader's baselines would pass checks against numbers it never produced.
- Ship the exact bytes you measured. Retyped rubrics are a new experiment nobody ran. Generating the requests from the harness and checking byte equality cost little and removed a class of doubt.
- Fail at startup, before spending money. An identity mismatch stops the job before any GPU or grading spend; a bad key stops it before the first Opus call.

## Caveats

- The 0.95 cutoffs were chosen from the same data we evaluated them on. A third trained model would show whether they hold.
- The out-of-scope (50) and regression (28) categories are too small to read on their own.
- Agreement is measured against Opus, not against humans. A sealed, hand-graded set covering every category is still to do.
- Billed grader cost is not recorded yet; the dollar figures are token-price estimates.

## Summary

- Grading cost per eval went from about $43.60 to about $11, a 75% saving, on grading only.
- Jev handles 60–62% of recall verdicts and 91–92% of non-recall verdicts at a 0.95 cutoff.
- On the rows it handles, Jev agrees with Opus 99.1–99.8%, against an Opus self-agreement floor of 98.7–99.6%.
- Without a cutoff, Jev accepted 7 of 148 kept-out answers Opus rejected; at 0.95 it accepted 0 on both models.
- Recall at the 0.90 cutoff missed the 98.7% bar on the second model (98.4%, 6 lenient vs 2 strict), so we raised the cutoff rather than the bar and gave up four points of saving.
- Version 1 saved 35% with the same per-verdict price; the rest came from extending coverage to non-recall categories.
