# Writing style guide

Target register: an engineer writing up results for other engineers. The reader is assumed to be skeptical, technically literate, and short on time. Think of a well-received Hacker News post or an internal engineering writeup, not a newsletter.

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

## Structure

1. **Setup** (1–2 paragraphs): what the system is, what was being measured, and why it matters, with a concrete scale anchor (cost, latency, count).
2. **`<!--more-->`** after the setup.
3. **Short version**: the result in 2–4 sentences, including the headline numbers. Readers should be able to stop here.
4. **Background** as needed: what the thing under test actually is, in mechanical terms. No marketing language.
5. **Method**: n, passes, conditions, metric. Pre-registered thresholds stated before results.
6. **Results**: tables first, one-sentence interpretation after each. Keep tables small and label units.
7. **Analysis / failure modes**: what the results mean, with a concrete example (quoted text, a specific case) where possible.
8. **Caveats**: bulleted. Be specific about what is and is not validated, sample sizes, circularity, coverage gaps.
9. **Summary**: bullets restating each finding with its number. Optional single closing sentence with the takeaway.

Section headings are plain labels ("Method", "Results: verdict accuracy", "Caveats"), not phrases or teasers.

## Numbers and evidence

- Every quantitative claim gets the number. Give n. Give both sides of a comparison.
- Pair a percentage with what it means in counts when the count is small ("0.5 points is one judgment in 200").
- When restyling or editing an existing post, do not change any figure, table, or quoted passage.
- Quote source material verbatim in a fenced code block rather than paraphrasing it.
- If a result is within noise, say so rather than reporting a winner.

## Things to include when relevant

- A pre-registered bar and whether it was met.
- The failure analysis, not just the failure.
- Methodological mistakes and how they were caught, stated as a rule the reader can reuse ("use an arbiter from a different model family").
- What a proper validation would look like if this one falls short.

## Front matter

```yaml
layout: post
category: <one category>
tags: [<3–6 tags>]
description: "<1–2 sentences, plain summary of the finding. No hook.>"
title: "<Descriptive title stating the subject, not the twist>"
```

Title test: a reader should know what the post is about from the title alone. "Evaluating Jev as a Replacement for an LLM Eval Grader" passes; "The Number I Wasn't Shopping For" does not.

## Formatting

- Markdown tables for any comparison of more than two numbers.
- Numbered lists for procedures and arms; bullets for caveats and summaries.
- Inline code for field names, config keys, and API types (`Choice`, `min_judge_confidence`).
- No emoji. No images unless they carry data a table cannot.
