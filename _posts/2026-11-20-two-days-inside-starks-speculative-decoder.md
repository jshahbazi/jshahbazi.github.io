---
layout: post
category: Apps
tags: [Stark, speculative decoding, Apple silicon, inference performance, local AI]
description: "I spent two days comparing Stark's speculative decoder with Sushi, profiling verification, and replacing expensive work around the model kernels. Stark's speculative rounds became 9 to 18 percent faster with unchanged greedy output, and its new default schedule avoids the workloads where a fixed draft depth loses time."
title: "Two days inside Stark's speculative decoder"
---

Sushi is another local inference engine for Apple silicon. On its published records, it decoded code at 146.2 tokens per second, while Stark ran a different pack of the same model family at 97.1 on an M5 Max. The packs were different, so this was not a matched benchmark, but they were both purpose-built for a similar performance class. Stark being 49.1 tokens per second behind still annoyed me. I read Sushi's source, profiled Stark, and spent two days working on the gap. The speculative decoder in Stark is now 9 to 18 percent faster at a fixed draft depth, with unchanged greedy output, and the default schedule now chooses how far to speculate on every round.

<!--more-->

Speculative decoding uses a small draft head to propose several tokens. The full model then verifies those tokens in one batched pass, accepts the matching prefix, and rolls its state back to the last accepted token if a guess was wrong. The tradeoff is straightforward: drafting more tokens can reduce the number of full-model passes, but verifying extra tokens costs time and a wrong guess produces no value.

Stark is the local inference engine I've built for Apple silicon. The Stark artifact identity and preparation profile identify the exact pack as `fabiogreter/Qwen3.8-Flash-Next-lily-q4-xl` at revision `0f94842e...`. It uses Lily's Q4 GDN and expert weights, with Q8 weights for attention, shared experts, readout, and embeddings. The artifact is 106,905,155,192 bytes and was image-loaded during the runs.

The Sushi assessment identifies its pack as `Qwen3.8-Flash-Next-Sushi-4bpw`, which uses EXL3 trellis-coded experts and an affine 8-bit trunk. All Stark measurements below use the Lily pack on one M5 Max. Sushi's column comes from its published records and source; I did not run Sushi. This is an investigation of the engineering differences, not a matched benchmark between the engines: the model packs, their weight formats, and the kernels that run them differ.

On Friday, Stark reached 119 to 123 tokens per second on code and 84 to 87 on prose. On the same kinds of published workloads, Sushi recorded 146.2 and 79.5 tokens per second. Every output hash in the Stark tests remained unchanged. The new default is a measured, adaptive schedule with prompt lookup, with explicit configuration to restore fixed-depth behavior.

In this post I cover the starting comparison, the profile that pointed in the wrong direction, the scheduling work that produced most of the gain, the rule used to choose a new default, and what remains unmeasured.

## Stark and Sushi side by side

|  | Sushi | Stark on Thursday | Stark on Friday |
|---|---|---|---|
| Model pack | `Qwen3.8-Flash-Next-Sushi-4bpw` | `fabiogreter/Qwen3.8-Flash-Next-lily-q4-xl`, revision `0f94842e...` | Same as Thursday |
| Plain decode, no speculation | About 62 tok/s | About 73 tok/s | Unchanged |
| The promise | A verified token is bit-identical to plain decode | The same promise | The same promise, still tested on the real model |
| Cost of checking one more drafted token | About 3 ms, by its own records | About 5.7 ms | About 5.6 ms. This is the one I could not move |
| How far it drafts | Chosen every round, up to 8 tokens | Fixed for the whole request, up to 3 | Chosen every round, up to 3, plus drafts copied straight from the prompt |
| Who does the bookkeeping | The GPU chains the draft steps and hands back a few integers | Every draft step sends a 248,320-value row back to the host | Greedy drafts chain on the GPU, and the host prepares the next pass while the GPU is busy |
| Undoing a wrong guess | Replays the accepted tokens from the saved state | Kept a full copy of the recurrent state for every drafted token | Replays, the way Sushi does |
| How it gets benchmarked | Greedy, on a tidy synthetic code corpus | Sampled, on whatever was available | Both. Sushi's benchmark was ported so the conditions can match |
| Headline, code | 146.2 tok/s | 97.1 | 123 |
| Headline, prose | 79.5 tok/s | 75.9, and speculation made it slower | 87 |

The largest visible gap was the cost of verifying an extra drafted token. A profile showed that verification consumed 80 to 90 percent of a speculative round. A plain decode step took about 14 ms, while checking one more drafted token added about 5.7 ms. Sushi's records put its comparable cost near 3 ms. That difference became the first target.

## The kernels that did not become faster

The profile split the 5.7 ms across three model stages, so I estimated that 15 to 19 percent of the total speed was available there. I attacked each stage separately.

- **Hyper-connections.** A shared-weight kernel was byte-identical to the original. It saved 0.06 to 0.25 ms per pass, too little to matter in the model, so I did not adopt it.
- **Routed experts.** Sharing experts selected by several rows was byte-identical as well. It tied on one half of the test and was slower on the other, so I rejected it.
- **Recurrent projections.** One variant was faster and passed 288 synthetic test cases. On the real model, it changed 3,476,470 values.

The third result is about exactness, not only performance. Stark's kernels use fast math, and the GPU compiler schedules the same arithmetic differently depending on the surrounding code. A kernel can pass a synthetic suite and still produce a different result when it runs as part of the model.

That matters because the verifier's probabilities must be bit-equal to plain decode. Exact sampling is the product guarantee; a faster kernel that is close is not usable. Sushi byte-tests each row kernel against its own one-row form. Stark uses a different kernel body for one row, so the two forms did not agree after the fact. Reaching Sushi's row cost probably requires replacing the plain-decode kernels too, which would change the reference bits and needs a separate qualification. I chose not to begin that work.

One scheduling idea from Sushi did help the kernels' surrounding work. Stark had been saving a copy of the recurrent state for every drafted token. It now saves one state and replays accepted tokens when a guess is wrong. That removed 113 MB of writes per extra row and about 226 MB of memory per request. The measured gain was 1.6 to 3.4 percent.

The profile also needs two limits. It says where time goes, not whether the work can be removed. Each stage might be bound by memory traffic, arithmetic, or the overhead of many small GPU launches, and each requires a different change. Stage timings came from an instrumented session, which changes scheduling, so all throughput figures here come from uninstrumented runs. Two of the three ideas had already been tried and rejected before this experiment; they are now rejected twice.

## The scheduling work that paid

A second path ignored the model arithmetic and examined everything between kernel calls:

- **Waiting.** Polling for the GPU instead of blocking on it saved about 2 ms per round.
- **Drafting.** Greedy draft steps now chain on the GPU in one submission, and only token IDs come back.
- **Sampling.** Vectorizing the greedy argmax reduced the sampler from 0.36 ms to 0.02 ms per call.
- **Idle time.** The host encodes the next pass while the GPU runs the current one.

None of these changes affects the model's arithmetic, so none can change a sampled probability or a greedy token choice. Measured against the unmodified engine in alternating sessions:

| Setup | Before | After | Change |
|---|---:|---:|---:|
| Greedy, 1 / 2 / 3 drafts | 81.1 / 89.1 / 87.5 | 95.3 / 104.8 / 103.1 | +17.6 / +17.5 / +17.8% |
| Sampled, 1 / 2 / 3 drafts | 75.5 / 76.4 / 66.1 | 86.8 / 85.2 / 72.2 | +14.9 / +11.6 / +9.2% |
| Speculation off, greedy / sampled | 73.9 / 75.1 | 74.6 / 75.2 | +1.0 / +0.1% |

Every output hash on every variant equaled the baseline. The kernel work that looked promising returned 2 or 3 percentage points; the scheduling work returned the rest.

I do not know why polling helped by 2 ms. The documented wake latency is 0.09 ms, and the measured result is repeatable but unexplained. The no-speculation row is the control: it moved by 1 percent or less, which argues against session noise as the cause of the speculative gains.

There is also one hardware-specific guard in the sampling path. The GPU flushes subnormal numbers and the host does not, so a GPU argmax can disagree with the host rule when the top value is zero or subnormal. The draft chain detects that case and reruns the step on the host. The machine was not specially quieted for these runs.

## Choosing the depth every round

There is no single good draft depth. On predictable code, the model accepted about 90 percent of what the draft head proposed, and drafting three tokens paid off. While continuing a novel, it accepted about half, and drafting two was slower than no speculation.

The adaptive planner estimates tokens per millisecond for each available round shape. It uses the acceptance rate observed at each draft position and a measured cost table for the model. It does not inspect the clock, so the same request produces the same schedule every time. Drafting remains capped at three because, at Stark's row cost, a fourth draft does not pay.

Prompt lookup is a second change. If the last few tokens match an earlier part of the prompt, Stark can propose what came next there without calling the draft head. This is useful when editing code or quoting a document, where copy-heavy input improved by 8 to 10 percent.

Both the adaptive planner and prompt lookup were adapted from Sushi. Sushi is MIT-licensed, and the ported benchmark carries its license notice.

The schedules were compared with no speculation, averaged over 12 combinations of prose and code, greedy and sampled generation, and three prompt lengths:

| Schedule | Score | Worst setup |
|---|---:|---:|
| One fixed draft | 1.193 | 1.07 |
| Two fixed drafts, the old default | 1.155 | 0.95 |
| Planner | 1.215 | 1.06 |
| Planner with lookup | 1.218 | 1.06 |

The planner does not beat the best fixed depth on every workload. It avoids the depth that is wrong for that workload. One fixed draft beat it by 5 to 7 percent on sampled prose, for example. The planner also explores: on prose, about one round in five tested zero or two drafts where one draft was the right choice the whole time.

The cost table came from one build of one model on one machine. A kernel change requires measuring it again. These figures do not transfer to another model pack without a new table.

## The rule for moving the default

Stark's default draft depth had changed twice before, and both changes were reverted. Before generating the results for this change, I wrote down the candidates, the test cells, and the rule that had to be met:

1. A candidate was out if any cell was more than 3 percent slower than no speculation.
2. The winner had to beat the current default by 2 percent overall.
3. It could not be more than 5 percent behind the current default in any single cell.

The experiment ran 648 requests. Every schedule saw the same text windows and seeds.

On the first pass, the planner had the best score, but the rule rejected it: it was more than 5 percent behind the old default in two cells. Those cells had only one and three valid samples because sampled requests at long context ended early. A window was discarded for every schedule if any schedule ended early.

I then added windows to every sampled long-context cell, not only to the two that failed, and recorded that plan before examining the new results. With nine valid samples in each cell, both cells were inside the bound and the rule passed. The old default itself failed the safety check: two fixed drafts were slower than no speculation on prose and had already been shipping that way.

Adding data after seeing an inconvenient result needs scrutiny. Applying the same addition to all four cells and recording the plan first is defensible, but the better rule for future runs is to choose the minimum number of valid samples per cell before the run. That requirement is now in the performance playbook.

One source window also ended at the final page of Pride and Prejudice. The model stopped, so every schedule scored zero tokens there. The desktop app can request at most two drafts for this model because its memory profile is bounded there. Re-running the rule with that limit passed and cost about 1 percent against a limit of three. This result still represents one model, one machine, and one sampled setting.

I also removed `ignore_eos` from the runs. It forces every sample to decode the same number of tokens, but early stopping did not occur in this corpus. The experiment now counts valid early stops instead.

## A natural-chat check

The first measurements continued source material that the model did not write: a novel and a code corpus. Both earlier changes to the default had failed on a natural long answer to a real request, so I ran that case before keeping the new schedule.

The check used 24 requests through the chat template: write a tic-tac-toe game, plan a marathon, and explain TCP, with up to 1,024 tokens each. Speed is relative to no speculation, in greedy / sampled order:

| Workload | Old default | New default |
|---|---:|---:|
| Coding | 1.36 / 1.38 | 1.39 / 1.37 |
| Planning | 1.14 / 1.15 | 1.15 / 1.15 |
| Prose | 1.20 / 1.20 | 1.21 / 1.20 |

The new default passed. It also changed the conclusion from the earlier corpus.

On ordinary chat responses, the new and old defaults were effectively the same speed. The 9 to 14 percent prose gain was real, but it came from continuing a novel. When the model wrote its own prose, the draft head accepted two proposals about 71 percent of the time, compared with about 45 percent on the novel. The old fixed depth was already suitable for those generated responses.

The accurate summary is narrower. Ordinary chat does not become faster from the new default. On source text the model finds hard to predict, the planner prevents speculation from losing time. On copied text, lookup can make it faster.

These were 24 requests I wrote, with short prompts, one turn, and no tools. Agent sessions containing tool output are not covered. Every response ran to the 1,024-token cap and none ended on its own. Greedy output was identical across all three schedules for all 24 requests.

## What changed

For Qwen3.8-Flash-Next in the pinned Lily 4-bit pack, the pull request makes the following changes:

- **Faster rounds.** Speculative rounds are 9 to 18 percent faster at any fixed draft depth.
- **A new default.** A request that enables speculation without naming a schedule gets the planner with lookup.
- **Unchanged greedy output.** Greedy output remained token-for-token identical on every tested path.
- **Different seeded samples.** A seeded sampled request with speculation enabled will not reproduce the previous build's text. The output distribution is the same, but the random draws are spent differently.
- **Two opt-outs.** Send `"mtp_policy": "fixed"` and `"mtp_lookup": false` on a request, or set `STARK_LILY_MTP_ADAPTIVE=0` when the worker starts.
- **One qualified model.** Only the pinned Lily 4-bit pack gets the new default. Other packs keep their existing behavior.

## What's next

The remaining gap is the 5.6 ms cost per extra row. Closing that distance to Sushi probably means using one set of kernels for plain decode and verification. Because that changes Stark's reference bits, it needs its own qualification rather than an incremental kernel patch.

Agent sessions are the next measurement priority. Tool output gets copied into answers throughout a session, which is where prompt lookup should provide the largest benefit, but it is not measured yet. Each additional model pack also needs its own cost table and gate before it can use the planner. The unexplained 2 ms polling gain needs a separate investigation.

The work now lives in a performance playbook that records what to try, in what order, and what each change returned or why it failed. The project contributor docs point to it, and the pull request contains 12 experiment records, the public aggregates behind every number in this post, and SHA-256 hashes for every private run file.

On Sushi's published code benchmark, Sushi remains faster at 146.2 tokens per second against Stark's 119 to 123. On the published prose workload, Stark is now at 84 to 87 against Sushi's 79.5. Those are not matched comparisons: the packs differ, and I did not run Sushi. What the source established was useful even without that comparison: Stark could remove work around the kernels, choose draft depth per round, and preserve every tested greedy output bit.
