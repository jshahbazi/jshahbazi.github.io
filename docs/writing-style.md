# Writing style guide

Target register: an engineering-blog explainer, in the manner of the Cloudflare blog (for example [Announcing Claude Managed Agents on Cloudflare](https://blog.cloudflare.com/claude-managed-agents/)). The writer is a team explaining what it did and why, patiently and in order, to a reader who is skeptical, technically literate, and short on time. The reader is an experienced software engineer, not necessarily an ML or evals specialist, so field jargon is replaced with plain words or explained once. Concepts are built up before they are used; results are stated, not revealed. Not a newsletter, not a paper, and not a personal essay.

Reference post: `_drafts/2026-10-20-turning-off-the-neurons-that-make-our-model-say-i-dont-have-that.md`. It uses the explainer shape described under Structure below, and is the register to aim for. `_drafts/2026-10-12-testing-subq-snap-on-two-jobs.md` (narrative shape) and `_posts/2026-10-06-testing-openai-decisions-api-as-an-answer-grader.md` (report shape) are earlier registers that are still acceptable for comparison-heavy posts, but new posts should default to the explainer shape. `_drafts/2026-09-20-the-number-i-wasnt-shopping-for.md` is the register we moved away from.

## Voice

- "We" by default. The team ran the experiment, built the field, shipped the fix. Use "I" only for a judgment or decision that is genuinely one person's and where that matters to the reader. Past tense for what was done, present tense for what is true.
- Declarative and patient. Each paragraph carries one idea, in two to four sentences. Explain the thing before giving the number about it.
- Orient, then deliver. Open a section by saying what it covers or what the reader needs to know, then give the result. Signposting is encouraged: one paragraph after the summary saying what the post will cover, and sentences like "A few details are worth calling out" before a list.
- State claims directly. Do not build suspense or withhold results for a reveal.
- No framing hooks. Do not open with what the post "started as" or "turned into", what it "reminded" you of, or what lesson it teaches. Open with what the thing is and what was tested.
- No kicker endings. Do not close on an aphorism, a callback, a turn of phrase, or "the thing I will carry forward". End with what you will do next, or a flat statement of the general point, and stop.
- No performed casualness. No sentence fragments used as paragraph openers ("The numbers.", "Some context.", "One method problem."), no one-line paragraphs used as beats ("Then the catch."), no self-deprecating asides ("this embarrassed me a little"), no "here's the whole thing in one paragraph", no "in case you're building something similar". Say the thing.
- If a sentence would work as the first or last line of a LinkedIn post, cut it.
- Prefer the plain word. "Cut" over "slash", "worse" over "took a hit", "cost" over "bill".
- No rhetorical questions, no puns or metaphors in headings or prose ("prime suspect", "neuron surgery", "closed that door").
- No hedging filler ("I think", "it seems like") unless the uncertainty is real, in which case say what is uncertain and why.
- Understated rather than emphatic. Let the numbers carry the weight. No bold for emphasis inside prose or tables; bold is reserved for lead-in labels in bullet lists (see Formatting).
- Admit mistakes and near-misses plainly, as method notes, not as confessions. "One sequencing mistake is worth recording." is the right register.

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

Three shapes are in use. Default to the explainer shape. Use the narrative or report shape only for posts that are mostly a comparison table of several models or tools.

### Explainer shape (preferred)

1. **Opening paragraph**: what the external thing is (a paper, a product, a technique) in one or two mechanical sentences, then the question we asked about our own system, then the answer in one plain sentence. No tease.
2. **`<!--more-->`**.
3. **Orientation paragraph** for readers new to the blog: what our system is, in three or four sentences. Skip only if the post needs none.
4. **Results paragraph**: every headline number, both sides of each comparison, and what we did about it. Readers should be able to stop here.
5. **Signpost paragraph**: one sentence or two saying what the post covers, in order ("In this post we'll go through X, walk through Y, and then cover Z.").
6. **Background sections**, one per concept the reader needs before the results. Each builds one idea: what the paper claims and what we took from it; how the relevant part of our system works; the distinction the experiment is meant to resolve. Keep each short.
7. **Method section**: what was fixed in advance, what was reused, what was audited, what it cost. A bulleted list with bold lead-ins works well here.
8. **Results section(s)**: in the order the work happened. Each gives the number, what it means, and the caveats that apply, in the same section. Do not defer caveats to the end.
9. **What we built and why** (if anything shipped): design choices as a bulleted list with bold lead-ins, then the tuning or validation table, then what was tried and rejected.
10. **Shipping and review**: what was merged, what review caught, how the fix was measured, and any sequencing mistake.
11. **What's next**: concrete next steps and the condition that would change the plan. One or two paragraphs. No bullet recap, no closing line, no lessons section.

### Narrative shape

1. **Opening paragraph**: what the thing is, in mechanical terms, and what was tested. One or two sentences placing it next to things the reader may already know from earlier posts. End the paragraph with the result in one plain sentence ("It did very well at one and not the other."), not a tease.
2. **`<!--more-->`**.
3. **Short answer** paragraph: the headline numbers, both sides of each comparison, and what you are going to do about it. Readers should be able to stop here.
4. **A method note** (one paragraph): what was reused, what was new, what was not changed after seeing scores, whether it was audited. Put it before the results so the reader knows how to weigh them.
5. **One section per test or topic**, in the order the work happened. Each section: what the test is, the table, what the numbers mean, and the caveats that apply to that result, in the same section. Do not defer caveats to the end; put them next to the number they qualify.
6. **A "why" section** if you have a hypothesis: say it is a hypothesis, give a concrete toy example, and say what would be needed to test it.
7. **Where this leaves things**: what you will use for what, and what would change your mind. One or two paragraphs. No bullet recap, no closing line.

### Report shape

1. **Setup** (1–2 paragraphs): what the system is, what was being measured, and why it matters, with a concrete scale anchor (cost, latency, count).
2. **`<!--more-->`** after the setup.
3. **Short version**: the result in 2–4 sentences, including the headline numbers.
4. **Background** as needed: what the thing under test actually is, in mechanical terms. No marketing language.
5. **Method**: how many cases, how many passes, what setups were compared, and what was measured, in plain words. Any bar you set in advance is stated here, before the results.
6. **Results**: tables first, one-sentence interpretation after each. Keep tables small and label units.
7. **Analysis / failure modes**: what the results mean, with a concrete example (quoted text, a specific case) where possible.
8. **Caveats**: bulleted. Be specific about what is and is not validated, sample sizes, circularity, coverage gaps.
9. **Summary**: bullets restating each finding with its number.

### Headings

Section headings are plain, descriptive labels. In the explainer shape they are topical noun phrases that name what the section explains ("An overview of the essay", "How our model learns to decline", "A blind spot in the scorer", "Introducing decline_class", "Keeping the rule honest", "Shipping it", "What's next"). In the narrative shape they name the subject ("The tool-picking test"); in the report shape they name the section type ("Method", "Caveats"). A question is acceptable when it is the literal question the section answers ("Absent or held back?"), not when it is a hook. No sentence-style headings that perform a voice ("Setting it up so I couldn't fool myself").

### Labels in prose

Internal dataset codes (`J0`, `E1`, arm names) belong in the harness, not the post. Write "without the source text" and "with the source text", or whatever the plain description is, and use it consistently in tables and prose. Keep the code only if a linked artifact uses it and the reader needs to match them up.

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
- Numbered lists for procedures and the variants being compared; bullets for caveats, design choices, and method details.
- Bullets may open with a short bold lead-in label followed by a period ("**Noise floor.** Regenerating the reference moved one verdict out of 376."). Use this for lists where each item is a distinct named point: method details, design choices, reasons for a decision, failure types. Do not use it for lists of rejected variants or plain caveats, and never bold inside running prose.
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

Full writeup, with the tables and caveats: https://johnshahbazian.com/cutting-answer-grading-cost-with-a-first-pass-grader
```
