---
layout: post
category: Evals
tags: [LLM evals, TypeSafe, Jev, open models, local inference, answer grading]
description: "We compared six open decision models against a saved Jev run on 100 hand-graded answers. JevK5-4B agreed with the human labels 89% of the time against Jev's 90%, with a median response time of about 162 ms on a Mac. It is now our preferred open model for further testing; production grading has not changed."
title: "Testing JevK5-4B as a Free, Local Alternative to Jev for Answer Grading"
---

Setup: at Brekko we turn a customer's documents into training data and train small models to answer questions about those documents. Evaluating a trained model means having a second model grade each of its answers. The grader receives a question, the known fact, the candidate answer, and a rubric, and has to tell a correct answer from one that changes a number, confuses two entities, or leaves out something the question asked for. For few days, we have been using TypeSafe's Jev for part of that job. Jev is a hosted service, and several open models now copy its interface. We wanted to know whether any of them could do our grading task on a machine we own.

<!--more-->

## Short version

We tested Jeff, Jeeves, Kev, Decider, and two sizes of JevK5 on the same 100 hand-graded cases we used to evaluate Jev. JevK5-4B agreed with the human accept/reject labels 89% of the time, against 90% for our saved Jev run, with a median local response time of about 162 ms on a Mac. None of the other open models came as close. Replaying the same cases through a packaged local server reproduced every verdict. We have picked JevK5-4B as our preferred open model for further validation and local experiments. Our production grading configuration has not changed.

## Background

[Jev](https://docs.typesafe.ai/introduction) does not write prose. You send it the input and a list of questions with fixed answer types, and it returns a decision and a probability for each option. Our answer judge is a single three-way choice: `correct`, `incorrect`, or `partial`. Software can consume that directly, with no verdict to extract from an explanation. I wrote up [how Jev compares to Claude as a grader](/evaluating-jev-as-an-eval-grader) earlier; this post is about the open models that imitate it.

The candidates were:

1. [Jeff](https://github.com/firelex/jeff), 0.8B parameters.
2. [Jeeves](https://github.com/PostHog/jeeves), 9B, tested with and without its reasoning mode.
3. [Kev](https://github.com/jaredpalmer/kev), 4B, from an earlier study.
4. [Decider](https://huggingface.co/Mapika/decider-4b), 4B, version 2.
5. [JevK5](https://github.com/allebee/jevk5), 4B (v0.3) and 9B (v0.3.3).

Each was run locally in the serving recipe we would actually use, which means they differ in numeric precision, input formatting, and runtime. Where that matters it is noted below.

## Method

The test set is Human100: 100 document-grounded recall cases, frozen and previously inspected, with 67 answers a person accepted and 33 a person rejected. Every model saw the same questions and the same fixed answers in two setups:

- J0: the fact, question, answer, named entities, and rubric.
- E1: the same, plus the original source text.

The score is accept/reject agreement with the human label. A `correct` verdict counts as accept; `incorrect` and `partial` both count as reject. Each completed local study sent every request twice. The models are deterministic, so the second pass checks stability; it does not turn 100 cases into 200 independent examples.

All response times are warm measurements on an Apple M5 Max with 128 GB of RAM, taken in separate sessions rather than a controlled throughput benchmark. The Kev timings are server-reported model time only; the other local rows include tokenization and reading the result back. The saved Jev run has no matched local measurement.

## Results: agreement with human labels

| Model / tested recipe | J0 human agreement | E1 human agreement | Median J0 / E1 response time |
| --- | ---: | ---: | ---: |
| Saved Jev | 90.0% | 88.5% | No matched local measurement |
| Jeff 0.8B, original release | 81.0% | 72.0% | 23 / 163 ms |
| Jeeves 9B, without reasoning | 84.0% | 85.0% | 887 / 3,870 ms |
| Kev-4B, earlier study | 82.0% | 74.0% | 212 / 796 ms* |
| Decider-4B v2, BF16 / MPS | 86.0% | 86.0% | 160 / 1,170 ms |
| JevK5-9B v0.3.3, Q8 / Metal | 82.0% | 88.0% | 311 / 1,938 ms |
| JevK5-4B v0.3, Q8 / Metal | 89.0% | 88.0% | 162 / 998 ms |

\* Server-reported model time, excluding tokenization and readout.

JevK5-4B is one point behind the saved Jev run on J0 and half a point behind on E1, and it is the fastest of the models that scored above 85%. "Q8" means the weights were shrunk to 8-bit numbers; "Metal" and "MPS" mean the Mac's GPU was used. The earlier Kev study used the same Human100 labels but a broader request that also asked secondary score questions, as did the saved Jev run.

## Results: agreement with a saved Opus run

We also ran the models on Recall224, a second set of 224 fixed answers. That set has saved Claude Opus judgments rather than human labels, so these numbers say how often each model agreed with Opus, not how often it was right.

| Model | Accept/reject agreement with Opus |
| --- | ---: |
| JevK5-4B | 91.96% |
| Decider v2 | 91.07% |
| JevK5-9B | 88.39% |
| Jeeves | 85.71% |
| Jeff | 85.27% |

The ordering matches Human100 at the top, with JevK5-4B and Decider v2 close together and the rest behind.

## What we found with each model

### Jeff

Jeff was the most tempting option on speed. A 0.8B model returning a short decision in roughly 23 ms would be useful if the decisions were good enough. On our task the original release reached 81% J0 agreement, and adding the source text dropped it to 72%.

We tried to close that gap by training it further on public decision data and fictional examples across several domains. Two initial attempts scored 78% on Human100 J0. A broader recipe that retrained the final block reached 80%. An adapter across the whole backbone fell to 47%, despite scoring 100% on the generated development set it was trained against. Along the way we found and corrected a difference in how inputs were formatted in an early synthetic evaluation; the corrected results still showed more wrong answers being marked correct. These experiments rule out the recipes we tried, not what Jeff can learn. They did make us unwilling to pick it on speed alone.

### Jeeves

Jeeves without reasoning was our strongest completed local contender before the later comparison. It improved on Jeff and did well on our synthetic tests. On Human100 it reached 84% J0 agreement and accepted 14 of the 33 human-rejected answers per pass. JevK5-4B accepted eight. In the recipes we measured, the 4B was also about 5.5 times faster on J0.

We tried Jeeves with reasoning turned on. We stopped the run after 185 judgments; the median response time was 44.6 seconds on our local BF16/MLX setup. On the cases it completed, reasoning improved J0 by one correct decision and left E1 unchanged. A partial run cannot establish the full model's accuracy or predict how it would perform on CUDA hardware. It gave us little reason to keep paying that local time cost.

### Kev and Decider

Both are credible alternatives with different strengths. Our older Kev-4B run reached 82% J0 and 74% E1. Decider v2 was much closer, at 86% in both setups, with a short-request response time essentially equal to JevK5-4B. Decider also passed a confidence screen on a second set where JevK5-4B failed (see "Confidence" below), so it deserves attention if the goal is deciding which cases a local model can handle alone.

We tested Decider v2 specifically. Its current model card says that v2.1's confidence scores track its accuracy less well on hard items. Neither v2.1 nor Kev-9B has been tested here; their absence from the table is work not yet done, not a negative result. Older studies also recorded djev at 89% J0 / 85% E1 and Laya at 63% as shipped, rising to 81% after training on Brekko labels. Those runs lack the same complete recipe and timing record, so they are kept separate from the table above.

### JevK5-9B

The larger JevK5 was a useful check. The tested 9B v0.3.3 release reached 82% J0 and 88% E1 while taking roughly twice as long as the 4B. More parameters did not improve the aggregate result on this workload.

## Replaying through the packaged server

The research harness is one thing; the serving path we would actually use is another. We replayed Human100 through our installed JevK5 MCP server (MCP is a standard protocol for exposing a tool to other software), making all 200 J0 and E1 decisions through that interface. Every verdict matched the previous 4B run. Probability differences were at floating-point rounding scale, with no inference errors and no cache hits. Median response times through the server were 165 ms for J0 and 901 ms for E1. An independent audit of the replay passed 1,237 checks. This shows the packaged service preserves the tested behaviour; it adds no new accuracy evidence.

## What "free" means here

JevK5-4B's [code](https://github.com/allebee/jevk5) and [released weights](https://huggingface.co/alibiserikbay/JevK5-GGUF) are Apache-2.0. The Q8 file we tested is about 4.48 GB and runs through llama.cpp on Apple Silicon, other supported GPUs, or a CPU. Our measurements used the Mac's GPU; we have not benchmarked a CPU deployment.

"Free" means downloadable weights and code with no per-decision fee to a model vendor. Hardware, electricity, operations, and any hosted fallback still cost money, and we have not measured fleet economics. For a model kept resident on hardware you already own, being able to run locally and control the serving environment is worth something before any cost saving is assigned to it.

## Confidence

In the earlier Jev post, the useful part turned out to be the confidence score: using it to decide which cases a cheap grader could settle alone, and sending the rest to Opus. We repeated that check for JevK5-4B. In a development replay on Human100, a two-stage setup with JevK5-4B in front of Opus settled 57% of decisions locally and reached 93.5% agreement with the human labels, matching the saved Jev two-stage setup at similar coverage.

The same cutoff did not hold on Recall224. It failed both our disagreement screen and our screen for wrong answers being marked correct, and a stricter cutoff settled too few cases to be useful. So the bar we wrote down for replacing the production grader is still unmet, and the confidence score needs its own validation before it can be used to route cases.

## What still needs work

- JevK5-4B still marks eight of Human100's 33 human-rejected answers as correct on J0.
- Its five-point lead over Jeeves has a paired 95% interval of −1 to +11 points. On 100 cases that is not enough to establish broad superiority.
- It returned no `partial` verdicts on Human100. Accept/reject agreement alone cannot certify all three grading labels.
- Separate fictional controls exposed a material omission it accepted, and its probabilities changed when equivalent options were reordered.

## Caveats

- Human100 is one reused development set of 100 cases. The numbers describe our workload, not arbitrary customer domains.
- The repeated passes check that the models are deterministic; they do not add independent cases.
- Recall224 agreement is against saved Opus judgments, not human labels.
- The models were run in different recipes (precision, formatting, runtime) on one Mac in separate sessions. The response times compare practical setups, not a controlled benchmark.
- Decider v2.1 and Kev-9B were not tested. The Jeeves reasoning run was partial.
- The results apply to the specific released versions named in the table.
- The MCP replay confirms the serving path reproduces the harness; it is not additional accuracy evidence.

## Summary

- On Human100, JevK5-4B v0.3 Q8 agreed with the human labels 89.0% of the time on J0 and 88.0% on E1, against 90.0% and 88.5% for the saved Jev run.
- Median local response time was 162 ms on J0 and 998 ms on E1; the packaged MCP server measured 165 ms and 901 ms and reproduced all 200 verdicts.
- The next-best open models were Decider v2 at 86.0% / 86.0% and Jeeves at 84.0% / 85.0%. Jeeves accepted 14 of 33 rejected answers per pass; JevK5-4B accepted eight.
- Jeff was fastest at 23 ms but reached only 81% J0 agreement, and our training attempts peaked at 80%.
- The 9B JevK5 scored 82% / 88% and took about twice as long as the 4B.
- On Recall224, JevK5-4B agreed with Opus 91.96% of the time, ahead of Decider v2 at 91.07%.
- A two-stage setup settled 57% of Human100 locally at 93.5% agreement, but the same cutoff failed our screens on Recall224, so the production replacement bar is unmet.

For anyone looking for a free, local Jev-style answer judge, JevK5-4B v0.3 Q8 is the model we would try first. Our next step is fresh human grading focused on omissions, factual near misses, partial answers, and the confidence cutoff.
