---
layout: post
title: "Same Answers, Different Score"
description: "Upgrading our eval grader moved recall 6.4 points on identical responses, without touching the model we actually train."
---

<style>
.entry table {
  display: block;
  overflow-x: auto;
  width: 100%;
  margin: 2rem 0;
  font-family: var(--mono);
  font-size: 0.82rem;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.entry table th {
  text-align: right;
  font-weight: 500;
  color: var(--muted);
  border-bottom: 1px solid var(--border-strong);
  padding: 0.35rem 0.9rem;
  font-size: 0.74rem;
  letter-spacing: 0.04em;
}
.entry table th:first-child,
.entry table td:first-child { text-align: left; white-space: normal; }
.entry table td {
  text-align: right;
  padding: 0.5rem 0.9rem;
  border-bottom: 1px solid var(--border);
  color: var(--text-soft);
}
.entry table tbody tr:last-child td { border-bottom: 1px solid var(--border-strong); }
.entry table strong { color: var(--accent); font-weight: 600; }
.entry .caption {
  font-family: var(--sans);
  font-size: 0.78rem;
  color: var(--muted);
  margin-top: -1.4rem;
  margin-bottom: 2rem;
}
</style>

We fine-tune a small model on customer documents to answer domain-specific questions. To evaluate how well it works, we run a few thousand questions through it and have a frontier model grade the answers. That score determines whether a model checkpoint is ready to ship.

Last week I upgraded our external API calls from Sonnet 4.5 and Opus 4.5 to Sonnet 5 and Opus 5. The model we train remained completely unchanged (a frozen open-weights checkpoint). I expected the grader upgrade to be neutral for our benchmark scores.

<!--more-->

To verify, I re-graded a set of saved responses using the exact same response files. Only the grader model changed.

| Probe set | Sonnet 4.5 | Sonnet 5 | Δ | Flipped |
|---|---|---|---|---|
| Varied phrasings (880) | 0.599 | 0.662 | **+0.064** | 7.7% |
| Terse user phrasings (880) | 0.406 | 0.469 | **+0.064** | 9.3% |
| Adversarial contamination (100) | 0.930 | 0.920 | −0.010 | 1.0% |

Both independent probe sets jumped by the exact same margin, and almost every flip went upward (`incorrect` to `partial`, `partial` to `correct`). Sonnet 5 simply graded the same text more leniently.

For comparison, grading the same responses twice with the *same* model usually flips around 1.1% of verdicts - essentially our noise floor. Here, flips were 7–8x higher and entirely directional.

There was also a potential confound: Sonnet 5 rejects explicit `temperature` parameters, so the re-grade ran with the provider's default temperature. Re-running the old model at that same default shifted scores by only +0.002 (six flips, well inside noise). The model upgrade itself accounted for +0.061 of the +0.064 jump.

## Whoever writes your eval questions is making a claim about your users

While digging into this, I ran another test on question formulation using the same model and 220 target facts across five different question sources.

| Who wrote the question | Recall | Declined | Median words |
|---|---|---|---|
| Verbatim from training | 0.966 | 0.000 | 19 |
| Our eval generator | 0.807 | 0.048 | 18 |
| A different generator | 0.599 | 0.173 | 14 |
| Wh-questions only | 0.714 | 0.107 | 14 |
| How people actually type | **0.406** | **0.325** | 7 |

<p class="caption">"How people actually type" = an LLM prompted to write the question a busy person would type into an internal assistant: terse, context omitted, sometimes a request rather than a question.</p>

We had been reporting an eval recall around 0.89. The model definitely knows these facts - it scores 0.966 when prompted using the exact phrasing it saw during training. But when asked those same facts in seven-word prompts resembling real user queries, recall drops to 41%, and the model declines to answer roughly a third of the time.

A metric like "overall recall" doesn't mean much without specifying how the questions were generated. That limitation was always there; testing multiple generation styles just brought it to the surface.

## Treating graders like instruments

The immediate fixes took under an hour, but the more important takeaway was how easily unversioned evaluation tooling can distort results.

- **Pin the grader version in eval metadata.** If you version probe sets and stability baselines, the grader model belongs in that same configuration tuple so changes require an explicit re-baseline.
- **Measure baseline grader variance.** Grading the same responses twice with the same model establishes an empirical noise floor. Without knowing our baseline ~1% flip rate, that 7.7% delta could easily have been mistaken for genuine model improvement.
- **Avoid unpinned model defaults in configs.** Our default model string had been updated weeks earlier, and we only avoided accidental score shifts because deployment manifests happened to pin the old version explicitly.
- **Smoke-test parameter compatibility.** Checking whether an API key works with a new model isn't enough; client wrappers need end-to-end tests with the exact payload kwargs used in production.
- **Vary question generation styles.** If benchmark questions are generated with the same prompts and model families used for training data, the benchmark often ends up evaluating stylistic familiarity instead of actual comprehension.

## Final thoughts

Language models end up in important areas all over the pipeline: grading responses, writing test questions, extracting facts. None of them face the customer, but they quietly drive every decision about what ships.  The littlest thing can ripple through the system and cause unexpected shifts in outcomes, so it's crucial to maintain rigorous versioning, testing, and monitoring practices throughout the entire workflow.
