---
layout: post
category: Evals
tags: [LLM evals, OpenAI, Decisions API, TypeSafe, Jev, JevK5, answer grading, cost]
description: "We ran OpenAI's new Decisions API through the same 100 hand-graded answers we used to test Jev and its open-source clones. It agreed with the human labels 83% of the time, against 90% Jev and 89% for JevK5-4B. Median response time was about 135 ms over the network and all 400 judgments cost about six cents. Most of the gap comes from rejecting answers a person had accepted."
title: "Testing OpenAI's Decisions API as an Answer Grader Against Jev and JevK5-4B"
---

![Human100 results for nine graders, with the OpenAI Decisions row outlined in red. OpenAI Decisions agreed with the human labels 83% / 82% on J0 / E1 with 16 / 18 and 14 / 22 false accepts / rejects over both passes and a median response time of 135 / 136 ms. Jev scored 90% / 88.5%, JevK5-4B 89% / 88%, Decider v2 86% / 86%, Jeeves 84% / 85%, JevK5-9B 82% / 88%, Jeff 81% / 72%, Clef-flash 80% / 79%, Strands Decider 73% / 68%.](/images/openai-decisions-human100.png)

Setup: Over the past few weeks I have written up [TypeSafe's Jev as that grader](/evaluating-jev-as-an-eval-grader), [Jev as a first-pass filter in front of Claude](/cutting-answer-grading-cost-with-a-first-pass-grader), and [six open models that copy Jev's interface](/testing-jevk5-4b-as-a-free-local-jev-alternative). Until this week Jev was the only hosted service of its kind from a vendor we would consider. OpenAI has now released its [Decisions API](https://developers.openai.com/api/docs/guides/decisions), which does the same job: you send it input and a typed question, and it returns a decision and probabilities instead of prose. We ran it through the same 100 hand-graded cases as everything else.

<!--more-->

## Short version

OpenAI Decisions with `gpt-6-luna` agreed with the human accept/reject labels 83% of the time without the source text and 82% with it. Our Jev run scored 90% and 88.5% on the same cases; JevK5-4B, the open model we picked last time, scored 89% and 88%. The OpenAI result is faster than anything we have measured (median 135 ms including the network round trip) and cheap (all 400 judgments cost about $0.063 at list price), but it rejected three to four times as many human-approved answers as Jev or JevK5-4B, and it let through about as many bad ones. It is a useful hosted speed and cost result. It does not replace Jev or JevK5-4B for this grading task.

## Background

The Decisions API is a separate endpoint, `POST /v1/decisions`, with a request made of three parts: a `model` (currently only `gpt-6-luna`), an `input` (text, images, or both), and a list of `questions`. Each question has a type: `predicate` (true or false, returns a probability), `choice` (pick one of your values, returns the choice, a probability per option, and a `confidence`), or `score` (rate against ordered levels, returns a weighted average). Nothing is generated, so you pay only for input, at $0.10 per million tokens. There is no explanation in the response. If you have read the earlier Jev post, this is the same shape as Jev's `Noul`, `Choice`, and `Score` questions.

Our answer judge is one `choice` question named `verdict` with the options `correct`, `incorrect`, and `partial`, in that order, with the rubric in the instructions. That is the same question we sent to Jev and to every open model, serialized the same way; the request hashes match the ones from the JevK5-4B run.

The docs describe the service as a public beta. Responses reported `gpt-6-luna` and no pinned version, so a rerun next month may not return the same answers.

## Method

The test set is Human100: 100 document-grounded recall cases, frozen, with 67 answers a person accepted and 33 a person rejected. As before, each case was sent in two setups:

- J0: the question, the known fact, the candidate answer, and the named entities, plus the rubric.
- E1: the same, plus the original source text.

Each setup was run twice, so each cell below is 200 judgments over the same 100 cases. The second pass checks that the service is stable; it does not add independent cases. The score is accept/reject agreement with the human label: `correct` counts as accept, and `incorrect` and `partial` both count as reject. A wrong answer marked correct is a false accept; a right answer marked wrong is a false reject.

Requests went out serially from one HTTP client with a 60-second timeout and no retries. Two public control cases were run first to confirm the adapter worked, then the 100 private cases. The plan was written down before any private call, and the rubric was not changed after seeing scores. Every competitor number is read from its saved, audited record; nothing else was rerun. An independent audit of the OpenAI run passed 54,672 checks with zero errors.

## Results: agreement with human labels

The graphic at the top of the post summarizes this table; there, FA is false accepts (a wrong answer marked correct), FR is false rejects (a right answer marked wrong), and the asterisk on Jev's timing marks a historical API measurement.

| Model / tested recipe | J0 agreement | E1 agreement | J0 false accept / reject | E1 false accept / reject | Median J0 / E1 response time |
| --- | ---: | ---: | ---: | ---: | ---: |
| Jev | 90% | 88.5% | 14 / 6 | 18 / 5 | 438 / 461 ms (historical API) |
| JevK5-4B v0.3, Q8 / Metal | 89% | 88% | 16 / 6 | 18 / 6 | 162 / 998 ms |
| Mapika Decider-4B v2, BF16 / MPS | 86% | 86% | 22 / 6 | 22 / 6 | 160 / 1,170 ms |
| Jeeves 9B, no reasoning / MLX | 84% | 85% | 28 / 4 | 30 / 0 | 887 / 3,870 ms |
| OpenAI Decisions, gpt-6-luna | 83% | 82% | 16 / 18 | 14 / 22 | 135 / 136 ms (API) |
| JevK5-9B v0.3.3, Q8 / Metal | 82% | 88% | 22 / 14 | 20 / 4 | 311 / 1,938 ms |
| Jeff 0.8B, original / MLX | 81% | 72% | 24 / 14 | 52 / 4 | 23 / 163 ms |
| Clef-flash 9B, BF16 / MPS | 80% | 79% | 34 / 6 | 36 / 6 | 392 / 2,493 ms |
| Strands Decider 2B v19, BF16 / MPS | 73% | 68% | 54 / 0 | 64 / 0 | 309 / 825 ms |

Error counts cover both passes, so the denominators are 66 human-rejected and 134 human-accepted judgments per column. Clef-flash and Strands were tested after the last post and are included for completeness. Accepting everything scores 67% on this set, so 83% is well above the floor but in the middle of the pack, between Jeeves and the 9B JevK5. The local response times are warm measurements on a Mac from separate sessions; the OpenAI figure includes the network. They compare practical setups, not matched hardware.

## Results: which way it errs

The error columns are more informative than the totals. Per pass:

| Grader | J0 false accepts (of 33) | J0 false rejects (of 67) | E1 false accepts (of 33) | E1 false rejects (of 67) |
| --- | ---: | ---: | ---: | ---: |
| OpenAI Decisions | 8 (24.2%) | 9 (13.4%) | 7 (21.2%) | 11 (16.4%) |
| JevK5-4B | 8 | 3 | 9 | 3 |

On J0 the two graders let the same number of bad answers through, eight of 33. The six-point gap in agreement is entirely false rejects: OpenAI marked nine good answers wrong where JevK5-4B marked three. Adding the source text moved OpenAI in the usual direction for false accepts (eight down to seven) but made it reject more good answers (nine up to eleven). So it is stricter than Jev or JevK5-4B, not more discerning: a stricter grader that was also catching more bad answers would be a reasonable trade, and this one is not.

Per pass, J0 returned 66 `correct`, 6 `partial`, and 28 `incorrect`; E1 returned 63, 9, and 28. It does use the `partial` label, which JevK5-4B never did on this set. Both passes returned identical verdicts on every case, with zero refusals and zero API errors across 400 calls.

The responses include a `confidence` field and per-option probabilities. We stored and checked them but did not fit or test a cutoff for sending uncertain cases to Claude, so nothing here says whether that score is usable the way Jev's turned out to be.

## Is the six-point gap real?

Paired differences, OpenAI minus the comparator, in percentage points, with 95% intervals from resampling the 100 cases (both passes of a case stay together):

| Comparator | J0 difference | E1 difference |
| --- | ---: | ---: |
| Jev | −7 [−13, −2] | −6.5 [−13.5, 0.5] |
| JevK5-4B | −6 [−14, 2] | −6 [−15, 3] |
| Decider-4B v2 | −3 [−11, 5] | −4 [−12, 4] |
| Jeeves 9B | −1 [−10, 8] | −3 [−12, 6] |
| Jeff 0.8B | 2 [−6, 10] | 10 [0, 21] |
| Strands Decider 2B | 10 [−1, 21] | 14 [3, 26] |

The gap to the Jev run on J0 is the one comparison whose interval excludes zero. Against JevK5-4B, the six-point gaps have intervals that cross zero: on the first pass there were six cases only OpenAI got right and twelve only JevK5-4B got right on J0 (seven versus thirteen on E1), which on 100 cases is suggestive, not conclusive. What can be said with more confidence is the direction of the errors, since the false-reject counts are not close. These are unadjusted comparisons on one reused development set; they do not rank the services in general.

## Results: response time and cost

| OpenAI HTTP response time | J0 | E1 |
| --- | ---: | ---: |
| Median | 135 ms | 136 ms |
| Mean | 153 ms | 152 ms |
| P95 | 242 ms | 232 ms |

Timing covers the HTTP round trip and reading the full response, measured serially from one client. The E1 median, with roughly 2,300 to 4,100 input tokens per request, is about one-seventh of JevK5-4B's saved local E1 median on a Mac, and the response time barely moved between the short and long inputs. That is the strongest result in this test. It is a workload timing, not a throughput benchmark; we did not test concurrency.

| Usage and cost at list price | J0 (200 decisions) | E1 (200 decisions) |
| --- | ---: | ---: |
| Input tokens | 81,386 | 549,316 |
| Input tokens per request | 338–505 | 2,257–4,143 |
| Estimated cost | $0.0081 | $0.0549 |
| Estimated cost per 1,000 decisions | $0.041 | $0.275 |

The 400 private decisions used 630,702 input tokens, for about $0.063 at the published $0.10 per million input tokens. There are no output, cache, or reasoning token charges; the figure is computed from reported usage, not an invoice, and regional and long-context premiums can apply. For scale, the eval from [the cost post](/cutting-answer-grading-cost-with-a-first-pass-grader) graded about 2,350 answers with Opus for about $43.60; at the E1 rate above, 2,350 decisions would be about $0.65. Jev's list price is $0.042 per million input tokens, so OpenAI's per-token rate is about 2.4 times higher, though the two services count tokens differently and we did not measure Jev's usage on this set.

## Caveats

- Human100 is one reused development set of 100 cases, all straightforward fact-recall questions. The numbers describe our workload.
- The repeated passes check stability; they do not turn 100 cases into 200 independent ones.
- The service is in public beta with one model alias and no pinned version. The results apply to what `gpt-6-luna` returned on 2026-10-06.
- The six-point gap to JevK5-4B has a 95% interval that crosses zero. The difference in false-reject counts (18 versus 6 on J0) is the more solid finding.
- Only the OpenAI run is new. Every other row is a saved result, and the response times were measured on different hardware, in different sessions, with and without a network in the path.
- The `confidence` field was recorded but not tested. We cannot say whether a two-stage setup with Decisions in front of Claude would work.
- Cost is estimated from reported token usage at the base rate, not billed.
- Nothing in our production grading configuration has changed.

## Summary

- On Human100, OpenAI Decisions with `gpt-6-luna` agreed with human accept/reject labels 83% of the time on J0 and 82% on E1, against 90% / 88.5% for the Jev run and 89% / 88% for JevK5-4B.
- Per pass it marked 8 of 33 bad answers correct on J0, the same as JevK5-4B, but marked 9 of 67 good answers wrong where JevK5-4B marked 3. With source text that became 7 and 11.
- Both passes returned identical verdicts on all 100 cases; 400 calls, zero errors, zero refusals.
- Median response time was 135 ms on J0 and 136 ms on E1 including the network round trip, with a P95 under 250 ms. The long-input median was about one-seventh of JevK5-4B's local figure.
- All 400 judgments used 630,702 input tokens, about $0.063 at $0.10 per million, or roughly $0.041 per 1,000 short decisions and $0.275 per 1,000 with source text.
- Its confidence score was stored but not tested, so no first-pass-filter result is available yet.

For this grading task we are staying with Jev hosted and JevK5-4B locally. The Decisions API is the fastest and one of the cheapest options we have measured, and if a later version closes the false-reject gap it would be worth a second look, with the confidence score tested at the same time.
