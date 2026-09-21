# Writing style guide

Target register: an engineer writing up results for other engineers. The reader is assumed to be skeptical, technically literate, and short on time. They are an experienced software engineer, not necessarily an ML or evals specialist, so field jargon should be replaced with plain words or explained once. Think of a well-received Hacker News post or an internal engineering writeup, not a newsletter and not a paper.

Reference post: `_drafts/2026-09-20-evaluating-jev-as-an-eval-grader.md`. The earlier version at `_posts/2026-09-20-the-number-i-wasnt-shopping-for.md` is the same material in the register we are moving away from; diff the two to see the intended changes.

## Voice

- First person, past tense for what was done, present tense for what is true.
- State claims directly. Do not build suspense or withhold results for a reveal.
- Prefer the plain word. "Cut" over "slash", "worse" over "took a hit", "cost" over "bill".
- No rhetorical questions, no one-line paragraphs used as beats ("Then the catch."), no puns or metaphors in headings.
- No hedging filler ("I think", "it seems like") unless the uncertainty is real, in which case say what is uncertain and why.
- Understated rather than emphatic. Let the numbers carry the weight. Avoid bold for emphasis inside prose and inside tables.
- It is fine to say "So: no." or "That is circular." Dry is good; clever is not.
- Admit mistakes and near-misses plainly, as method notes, not as confessions.

## Vocabulary

Write for an engineer who has never run an eval. Use the everyday word when one exists; if a technical term is genuinely needed, define it in the sentence where it first appears and then use it consistently.

Avoid these unless defined:

| Instead of | Write |
|---|---|
| arm, condition (experimental) | variant, setup, filter, the X version |
| calibrated, calibration | "when it says it is unsure, it is usually wrong" (describe the behaviour) |
| arbiter, adjudicate | tiebreaker, settle disagreements |
| cascade, router, routing | first-pass filter, two-stage setup, decide which cases go to X |
| post hoc, held-out, pre-registered | after the fact, a separate set, wrote down beforehand |
| oracle | "if you could pick the better grader for each case" |
| n=100, within noise | 100 cases, too close to tell apart |
| false accept / false reject | marked a wrong answer correct / marked a right answer wrong |
| frontier model | large commercial model (name it) |
| latency | response time |
| adversarial probes | trick questions designed to catch the model out |
| non-autoregressive, fan-out, state blob | describe what it does instead |
| fine-tune, checkpoint | train, each trained model (unless the post is specifically about training) |

API types, field names, and config keys are the exception: keep them verbatim in inline code (`Choice`, `Noul`, `min_judge_confidence`) and explain them on first use.

## Structure

1. **Setup** (1–2 paragraphs): what the system is, what was being measured, and why it matters, with a concrete scale anchor (cost, latency, count).
2. **`<!--more-->`** after the setup.
3. **Short version**: the result in 2–4 sentences, including the headline numbers. Readers should be able to stop here.
4. **Background** as needed: what the thing under test actually is, in mechanical terms. No marketing language.
5. **Method**: how many cases, how many passes, what setups were compared, and what was measured, in plain words. Any bar you set in advance is stated here, before the results.
6. **Results**: tables first, one-sentence interpretation after each. Keep tables small and label units.
7. **Analysis / failure modes**: what the results mean, with a concrete example (quoted text, a specific case) where possible.
8. **Caveats**: bulleted. Be specific about what is and is not validated, sample sizes, circularity, coverage gaps.
9. **Summary**: bullets restating each finding with its number. Optional single closing sentence with the takeaway.

Section headings are plain labels ("Method", "Results: grading accuracy", "Caveats"), not phrases or teasers. A question is acceptable when it is the literal question the section answers ("Is the confidence score any good?"), not when it is a hook.

## Numbers and evidence

- Every quantitative claim gets the number. Say how many cases. Give both sides of a comparison.
- Pair a percentage with what it means in counts when the count is small ("0.5 points is one judgment in 200").
- When restyling or editing an existing post, do not change any figure, table, or quoted passage.
- Quote source material verbatim in a fenced code block rather than paraphrasing it.
- If a result is within noise, say so rather than reporting a winner.

## Things to include when relevant

- The bar you set before running, and whether it was met.
- Why it failed, not just that it failed.
- Mistakes in method and how they were caught, stated as a rule the reader can reuse ("use a tiebreaker from a different vendor than any grader being tested").
- What a proper validation would look like if this one falls short.

## Front matter

```yaml
layout: post
category: <one category>
tags: [<3–6 tags>]
description: "<1–2 sentences, plain summary of the finding. No hook.>"
title: "<Descriptive title stating the subject, not the twist>"
```

Title test: a reader should know what the post is about from the title alone, without knowing the field's vocabulary. "Evaluating Jev as a Replacement for an LLM Answer Grader" passes; "The Number I Wasn't Shopping For" does not.

## Formatting

- Markdown tables for any comparison of more than two numbers.
- Numbered lists for procedures and the variants being compared; bullets for caveats and summaries.
- Inline code for field names, config keys, and API types (`Choice`, `min_judge_confidence`).
- No emoji. No images unless they carry data a table cannot.
