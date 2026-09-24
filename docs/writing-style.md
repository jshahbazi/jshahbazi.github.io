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

## LinkedIn posts announcing a blog post

Each published post gets a LinkedIn post that stands on its own and ends with a link to the full writeup. The LinkedIn post is written for a broader audience than the blog: an engineer or engineering leader who scrolls past it in a feed, has probably heard of the product in the news, and has not read anything else on this blog. It should be understandable without clicking through, and it should make the reader want the tables and caveats.

The register is looser than the blog. Several blog rules are relaxed here on purpose; the rest still apply.

### What changes from the blog register

- Second person is expected. Address the reader directly ("your AI stack", "if you're optimizing for cost").
- Rhetorical questions are allowed as paragraph openers when the next sentence answers them plainly ("What does Jev do? Simply put, it makes decisions."). Use at most two or three.
- A stated opinion is allowed, and can be hedged ("I think that's the secret sauce."). One per post.
- Mild colloquialisms are fine ("secret sauce", "playing it safe", "the headlines") as long as the sentence around them is concrete.
- Name the alternatives the reader is likely using today (Sonnet, Luna, Opus, Sol), so they can place themselves in the story.

### What stays the same

- Every claim gets its number, and the numbers match the blog post exactly. Round for readability and flag the rounding ("~2,350", "about $43.60", "around 60%", "roughly 300ms").
- Plain words over field jargon. The Vocabulary table applies.
- No hype, no "excited to share", no exclamation marks, no bold, no emoji, no hashtags, no tagging people or companies.
- No suspense. The headline result appears in the first paragraph.

### Shape

Roughly 350–450 words, 9–11 short paragraphs of one to four sentences each. No headings, bullets, or tables. In order:

1. **Hook and headline result.** Open by placing the subject in something the reader already knows ("By now you've probably seen X in the headlines."), define it in one sentence, and give the two or three headline numbers in the same paragraph.
2. **What it does, mechanically.** One paragraph. Input, output, and what comes back.
3. **The obvious objection.** Name the familiar thing it resembles ("Astute readers may note that this sounds like a classifier."), say how it differs, and give your one opinion on why it works. Include a practical constraint if there is one (context limits, what makes it worse).
4. **Why the reader should care.** Where in their own stack this applies, and what they are probably doing there today, naming the models.
5. **Your position.** What you were doing before and what changed, in one or two sentences.
6. **The concrete case.** "Here's what that looked like in practice." State the pipeline, the scale, and the baseline cost.
7. **What you changed.** The mechanism and any threshold, in plain words.
8. **The result.** Coverage, agreement, and cost, before and after.
9. **The link.** A single line: "Full writeup, with the tables and caveats: <URL>". Nothing after it.

### Reference

The post for `_posts/2026-09-23-cutting-answer-grading-cost-with-a-first-pass-grader.md`:

```
By now you've probably seen TypeSafe's Jev in the headlines. Jev is a foundation model that makes structured decisions quickly and cheaply. Cheaply enough that we cut the cost of grading our model evals by 75%, and quickly enough that each decision comes back in roughly 300ms.

What does Jev do? Simply put, it makes decisions. You pass in a structured input and the set of possible outputs, and it picks one and tells you how confident it is.

Astute readers may note that this sounds like a classifier. And it is, with one difference: classifiers need training data, and Jev needs none. I think that's the secret sauce. They trained a massive, frontier-level model on everything, gave it a general understanding of the world, and pointed it at small, structured inputs. There are no huge context windows and no compaction. In fact, they warn that stuffing in too much information makes it worse, which forces you to be concise.

What does that mean for you? Somewhere in your AI stack, you are making LLM calls that boil down to a simple decision. If you're optimizing for cost, you're probably sending those to a cheaper model like Sonnet or Luna. If you're playing it safe, you're sending them to Opus or Sol.

I was sending mine to Opus. After some thorough testing, it turns out Jev can take over the vast majority of those calls, and in the rare case where it isn't confident, I hand the call back to Opus.

Here's what that looked like in practice. Our pipeline trains a small model on a customer's documents and evaluates it a few times per run. In one scenario, each eval had Opus grade ~2,350 answers, at about $43.60 per eval.

We put Jev in front of Opus as a first pass: Jev grades every answer and returns a probability for its verdict. If that clears 0.95, the verdict stands. Otherwise Opus grades it as before.

The result: Jev now handles around 60% of source-document questions and around 90% of the rest. On the rows it handles, it agrees with Opus 99.1–99.8% of the time, which is about as often as Opus agrees with itself. Cost per eval went from about $43.60 to about $11.

Full writeup, with the tables and caveats: https://jshahbazi.github.io/cutting-answer-grading-cost-with-a-first-pass-grader
```
