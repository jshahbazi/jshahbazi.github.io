---
layout: post
category: Evals
tags: [agents, Jev, Mercury, TypeSafe, decision models, conflict detection]
description: "We asked Inception's Mercury Decide and TypeSafe's Jev 1.13 the same question about 19 pairs of coding-agent assignments: if both agents carry out their work at the same time, could one overwrite or invalidate the other's changes? Mercury matched our expected answer on all 38 presentations; Jev matched 30. On the 20 presentations where both models were called fresh, it was 20 to 15."
title: "Testing Mercury Decide and Jev on Whether Two Agents' Changes Will Collide"
---

Inception's Mercury Decide and TypeSafe's Jev 1.13 are decision models. You send a structured input and a question with a fixed set of options, and the model returns one option, a probability for each option, and a confidence score. We used both to answer a question about our own multi-agent setup: when two coding agents carry out their assignments at the same time, can a model tell us beforehand whether one will overwrite or invalidate the other's work, even when the changes are in different files and produce no merge conflict? On the 19 pairs we tested, Mercury matched our expected answer every time, and Jev missed 8 of 38 presentations.

<!--more-->

Our system runs several coding agents against the same repository at once. Each agent gets an assignment and reports what it is doing as it goes. We want a step that looks at two in-flight assignments and says whether they will interfere, before either is merged. Until now that step was built on similarity, asking whether two agents were working on related or duplicate things, and that turned out to be a different question from the one we needed answered.

Here is what we found. Across four batches there were 19 pairs, each shown to each model twice (A then B, then B then A), for 38 presentations per model. Mercury matched the expected answer on 38 of 38. Jev matched on 30 of 38. That Jev number mixes two things: in the first two batches we reused saved Jev answers to the exact same inputs from earlier work, and in the last two we called both providers fresh. Restricting to the fresh calls, it is 20 of 20 for Mercury and 15 of 20 for Jev, over ten pairs. Jev's misses were concentrated in two places: conflicts that run through a contract across files, where it got 1 of 4 in the final batch, and compatible pairs that happened to touch the same file. Mercury also chose "insufficient" in both orders on both of the cases built to have no answer in the packet. These are counts from a development investigation on selected pairs, not a benchmark, and we found no Mercury error to study, so we are not changing our default yet. Mercury is the next thing we will evaluate properly for this step.

In this post we'll go through the kind of interference we are trying to catch, explain why similarity was the wrong question, show how the question was put to both models and how the batches were run, walk through the four batches and their results, cover what the confidence field actually measures, look at order effects and cost, and then say what we plan to test next.

## The kind of interference we are trying to catch

Agent A adds a new parameter to a Python function, and puts it before an existing positional parameter. Agent B, working from the same starting point, writes a caller that passes `0` positionally, intending it to mean "require fresh data." Each change is fine on its own. Together, B's `0` now lands on A's new parameter, and the freshness requirement silently falls back to the old default. The edits are in different files, so there is no merge conflict to catch, and a test that only looks at one side passes.

That is the case the rest of this post is organized around: two edits that are each correct alone, in different files, with no merge conflict, that break each other when combined. A similarity check does not see it, because the two assignments do not look alike. This pair is one of the six new cases in the final batch below. Mercury said "yes, these interfere" in both orderings. Jev said "no" in both.

## Why similarity was the wrong question

The obvious way to notice that two agents are working on the same thing is to embed their reports and compare vectors, and we had already tried that with Harrier and others. Embeddings were good at "are these related" (Harrier scored 0.924 on average precision, a ranking measure, against Jev's 0.900 on a 95-pair related-work set) and not good at anything more specific than that. Jev did better at "did these two agents do the same work." Neither was answering whether two agents were about to break each other.

Much of the time between October 15 and 19 went into separating questions we had been bundling together. "Two agents work on authentication" is related work. "Two agents implement the same requested check" is a repeated contribution. "A writer changes a format a reader depends on" is a contract interaction across different files. "Both patches replace the same old branch" is a mechanical merge conflict. "A stale replacement silently removes an accepted change" is the problem we care about, and it depends on checkout identity and how the write actually happens. A shared file does not imply any of these, and different files do not rule them out.

Some of the trouble was ours, and is worth recording. A pipeline audit found that our serialization was rewriting the declared order of the answer options, a deduplication check was comparing source text against escaped JSON, and a legacy evaluator had misread 182 positive related-work decisions. Fixing the plumbing cut input tokens on real pairs by 31.1% but did not, on its own, produce a measurable quality gain, so the bugs do not account for every bad answer. We also tried several ways of giving the model more or better-shaped context (compact "claim cards," source passages, observation logs), and none of them improved results across the board; each one recovered some matches and lost others. The first version of a graph-based grouping replay turned 173 direct links into 405 co-member pairs by chaining A–B and A–C into B–C, which is a structural error, not a model error.

The simplification that stuck was to stop asking about similarity and ask one question about interference, with an explicit third option for "you have not given me enough to say."

## The question we asked

Both models were sent a `state` containing the shared context plus Task A and Task B, and one `choice` question with three options:

```text
If these agents carry out these assignments at the same time, is there
evidence that one could overwrite or invalidate the other's intended
changes? A shared project or file alone is not enough.
```

| Option | Criterion |
|---|---|
| `yes` | The supplied evidence identifies intended changes to the same concrete code or shared resource that could overwrite, contradict, or invalidate one another. |
| `no` | The supplied evidence shows compatible intended changes or changes to different code or resources. |
| `insufficient` | The assignments lack enough detail about the targets or intended changes to judge interference. |

Mercury went to `https://api.inceptionlabs.ai/v1/decisions` as `mercury-decide`; Jev went to `https://api.typesafe.ai/v1/systemone` as `jev-1.13.0`.

## How the batches were run

A few details are worth calling out.

- **Two orderings per pair.** Each pair was presented twice, A then B and then B then A. Swapping the order means swapping which task is A and which is B, with each task's context moving with it. The options stayed in the same order. Nineteen pairs gives 38 presentations per model.
- **Expected answers kept out of the request.** Case names, rationales, and expected answers were never in the request body.
- **Saved versus fresh answers.** In batches 1 and 2 we reused saved Jev answers to the exact same inputs from earlier work and called Mercury fresh. In batches 3 and 4 both providers were called fresh. That makes 58 fresh HTTP calls in total: 38 to Mercury and 20 to Jev.
- **One attempt per entry.** No selective retries. The later runners checked the served model name, that the chosen option was in the option set, that probabilities were finite and summed correctly, and that the chosen option was the highest-probability one. None of the 58 fresh calls failed any of those checks.
- **An earlier wording mistake.** In a previous round some of our questions asked about overwriting while the `yes` option still described broadly shared work, including complementary changes. The models were, reasonably, answering the option text. We aligned the question and the criteria before any of the batches below.
- **Dates.** Batches 1 through 3 ran on October 17 and batch 4 on October 19. The dates are reconstructed from the conversation and archive timestamps, since the quick runners did not keep server timestamps.

## Four batches

| Batch | What was in it | Mercury | Jev | Jev source |
|---|---|---:|---:|---|
| 1 | Four hand-written controls: 3 conflicts, 1 compatible | 8/8 | 8/8 | Saved answers to identical inputs |
| 2 | Five real concurrent checkpoints from our logs, all compatible | 10/10 | 7/10 | Saved answers to identical inputs |
| 3 | Four historical patch pairs: 2 conflicts, 2 compatible, with same-base assumptions spelled out | 8/8 | 7/8 | Fresh calls |
| 4 | Six new synthetic cases: 2 conflicts, 2 compatible, 2 insufficient | 12/12 | 8/12 | Fresh calls |

Before the per-batch detail, the limits of these counts. The pairs were a mix of selected historical examples from our own agent logs, scenarios we wrote by hand, and six new synthetic cases we wrote specifically to be subtle. The two orderings of a pair are not independent, some source families recur, and a human has not yet gone over every expected answer. Nineteen pairs do not say how often either model is right in production. What they do show is that Mercury handled the distinctions we tested, including "there is not enough information here," more consistently than Jev did, and that we could not find a Mercury mistake in the cases we had planned. We also did not go looking for more cases until one appeared, so we still do not know where it breaks.

### Batch 1: four hand-written controls

These were scenarios from an internal writeup of overwrite cases, with the missing assumptions filled in before testing. A Redis writer switching to versioned keys while a reader still reads legacy keys, on the same instance and namespace, with no adapter. Two validators inserted into different places in the same file. An audit hook added to a function that a retry change replaces wholesale, with no context check. A currency helper changed to treat its input as cents while the caller still passes dollars. Three conflicts and one compatible pair.

Both models got all eight presentations right, so this batch did not separate them on answers. It did separate them on certainty. On the currency pair, Jev's probability of "yes" was 56% in one order and 84% in the other. Mercury's confidence field was 99.98% and 99.91%. Those are different fields, which the confidence section below explains, but the gap was large enough to notice.

### Batch 2: five compatible pairs from our logs

Five pairs of agents that had actually been running at the same time in our projects, where two AI reviewers, working independently, agreed the work was compatible. This batch was deliberately all compatible pairs. Mercury said "no" on all ten presentations. Jev's saved answers said "yes" three times: on a pair touching shared authorization code in both orders, and on a pair of planning documents in one order.

The authorization pair is the one to look at. Both agents edited the same file, but there was an explicit `TransferGrant` exemption that let both intended changes stand. That is exactly the "a shared file alone is not enough" case the question was written for. Mercury's confidence on those two pairs was lower than on the batch 1 controls, 76.74% to 98.18% on the planning pair and 78.71% to 93.85% on the authorization pair. That is consistent with the model being less sure on a harder case, but with zero Mercury errors and only one class in the batch there is no way to tell appropriately-less-sure from just-less-sure.

### Batch 3: historical patches with the assumptions written down

Two historical pairs that had hit mechanical conflicts, and two pairs of localized edits to the same file (one Rust, one Python) that had coexisted fine. Reusing old saved Jev answers would not have been a fair comparison after we changed the context, so both providers were called fresh. The framing told the models to assume both edits were made independently from the same base, with no handoff, and that both had to survive integration. That makes this a conditional test about patch interference under stated assumptions, not a claim that the historical agents actually overwrote each other.

Mercury matched all eight. Jev missed one: a pair where one agent added a journal event inside a readiness handler and the other replaced that same branch with runtime admission checks. Jev said "no" with A first and "yes" with B first. The wrong "no" had a 56% probability and a 34% confidence, so it was a low-confidence miss rather than a confident one. Jev's earlier answers on that same pair, before we added the framing, were "yes" both times. Input and run both changed, so the flip cannot be attributed to the framing alone.

### Batch 4: six new cases written before any calls

We wrote these ourselves, fixed the expected answers, had a second AI agent review them, and kept names, rationales, and expected answers out of the request body. Hashes of the cases and the runner were recorded before the calls and checked after.

| Case | Expected | Mercury (A/B, B/A) | Mercury confidence | Jev (A/B, B/A) | Jev confidence |
|---|---|---|---:|---|---:|
| Positional-argument binding | yes | yes / yes | 95.81% / 92.51% | no / no | 79.00% / 69.00% |
| Signature vs. transmitted JSON bytes | yes | yes / yes | 98.62% / 98.99% | no / yes | 38.00% / 49.00% |
| Keyword-only option under a timing decorator | no | no / no | 99.94% / 99.97% | no / no | 79.00% / 74.00% |
| Defaulted dataclass field plus keyword factory | no | no / no | 99.33% / 99.09% | no / no | 89.00% / 82.00% |
| Unknown API version / response adapter | insufficient | insufficient / insufficient | 99.89% / 99.89% | insufficient / insufficient | 14.00% / 27.00% |
| Unknown Redis instance mapping | insufficient | insufficient / insufficient | 99.91% / 99.90% | insufficient / yes | 64.00% / 23.00% |

Mercury: 12 of 12. Jev: 8 of 12, which breaks down as 1 of 4 on the two subtle conflicts, 4 of 4 on the compatible same-file edits, and 3 of 4 on the missing-context cases.

The two conflicts both required following a contract across files. The positional-binding case is the one described at the start of the post. In the signature case, one component rewrites the JSON it sends into a canonical form while another component signs the old insertion-order bytes; the server verifies the transmitted bytes, so the signature contract breaks. Both have simple executable checks (bind the new signature and watch the old default stay in place; serialize both ways and compare bytes), so we are confident in the expected answers. Whether cases like these are common in real agent traffic is a separate question we did not measure.

The two "insufficient" cases were built so that the answer depends on a fact not in the packet. A field rename affects API v2 only, and nothing says which version the client uses. A cleanup job and the login code read different Redis environment variables, and whether those resolve to the same database determines whether sessions get deleted. Mercury chose "insufficient" in both orders for both. Jev did so three times out of four and said "yes" once on the Redis case.

## What the confidence field measures

Both APIs return a chosen label, a probability for each label, and a scalar `confidence`. These are three different things, and we had been loose about them in earlier discussion. TypeSafe [documents](https://docs.typesafe.ai/confidence) the `Choice` confidence for n options as `(p_max − 1/n) / (1 − 1/n)`, which with three options is:

```text
confidence = (3 * p_max - 1) / 2
```

So a 56% top-option probability is a 34% confidence, and 84% is 76%. The "56% / 84%" quoted for the currency pair in batch 1 were option probabilities, not confidence. Mercury's documentation says its confidence is a value between zero and one and does not give a formula, but across all 38 saved Mercury responses the returned confidence matches that same three-option formula to a maximum absolute difference of 4.44e-16. That is an observation about what the API currently returns, not a documented guarantee.

Two consequences follow. First, 99.9% confidence in "insufficient" is coherent: Mercury is saying it is very sure the evidence does not settle the question, not that there is a 99.9% chance of an overwrite. Any workflow built on this needs to keep that third class instead of mapping everything that is not "yes" to "safe." Second, none of this says whether the confidence is right. We have no Mercury errors to look at, no representative sample, and almost no near-boundary cases, so "its confidence dropped on the hard pairs" means exactly that and nothing more.

## Swapping the order

Mercury's chosen label agreed across both orders on all 19 pairs. Its probabilities did not hold still: the planning pair in batch 2 moved by about 21.4 percentage points between orders, and the authorization pair by 15.1. Jev's chosen label disagreed with itself across orders on one pair in batch 2, one in batch 3, and two in batch 4.

An obvious rule would be to send both orders and keep the more confident answer. Nothing here validates that. Confidence moved with framing in both models, and two orders agreeing does not make them right. For now we keep both answers and surface the disagreement rather than pick one.

## Speed and cost

There were 58 fresh HTTP calls: 38 to Mercury and 20 to Jev. Mercury reported 65,623 input tokens and 38 output tokens; fresh Jev reported 25,150 input and 869 output. On the two batches where both were called fresh, Jev had the lower median response time: 0.162 s versus 0.517 s in batch 3, and 0.173 s versus 0.243 s in batch 4. That was run with two workers from one machine without controlling for network path, server load, or request order, so it is not a measurement of intrinsic speed, but Mercury was not faster in anything we observed.

At the prices listed on October 19 (Mercury Decide at a promotional $0.02 per million input tokens, $0.04 regular, output free; Jev 1.13 at $0.042 per million input, output free), the whole exercise came to about $0.00131246 for Mercury, or $0.00262492 at the regular rate, and $0.00105630 for the fresh Jev calls. Different tokenizers mean the same text does not produce the same billable count, so the token totals are not directly comparable either.

For scale, the earlier large Jev campaign that preceded all of this used 69,250,066 input tokens, about $2.91 at the listed rate. Long pair contexts, times both orders, times several questions, times many experimental revisions, add up even when each individual decision is tiny.

## What's next

We are not changing the default. What these four batches support is that Mercury Decide should be the next thing we evaluate properly for the second stage of this workflow (find candidate pairs cheaply, then ask a decision model about concrete interference), and that Jev 1.13, under this question and these inputs, missed indirect contracts across files more often than we can accept for that stage. Jev was still the better duplicate-work ranker in earlier tests, and it was faster here. We did not test Jev 1.14, which TypeSafe lists as a preview; the stable `jev-latest` alias still points to 1.13.

The result that would most change the plan is finding where Mercury fails, because a perfect score on 19 selected pairs is a reason to build a harder test, not to stop. The next version needs a fresh set frozen before any calls, with human-reviewed conflict pairs and pairs that differ by a single binding, unit, or resource identity; cases where the missing evidence is implicit rather than signposted; identical-input repeats kept separate from order swaps, so we can tell noise from framing; and a separate set, large and representative enough to check whether a 90% probability is right about 90% of the time, with the full probability distributions kept. It also needs to run through the whole pipeline, retrieval included, since these batches handed the models known pairs and skipped the part where you have to find them.
