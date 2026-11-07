# Writing style guide

This blog uses two registers. Pick one before drafting and do not blend them.

- **Explainer** (default): for experiments, evals, comparisons and anything where the reader needs to weigh evidence. Patient, declarative, caveats next to numbers. Described in the sections from Voice through Formatting.
- **Launch**: for announcing something the author built and is releasing. Short, direct, second person, benefit first, confident. Described under "Launch register" near the end. Everything in "Say it, don't announce it", "Numbers and evidence" and "Formatting" still applies to it.

The explainer register is an engineering-blog explainer, in the manner of the Cloudflare blog (for example [Announcing Claude Managed Agents on Cloudflare](https://blog.cloudflare.com/claude-managed-agents/)). The writer is a team explaining what it did and why, patiently and in order, to a reader who is skeptical, technically literate, and short on time. The reader is an experienced software engineer, not necessarily an ML or evals specialist, so field jargon is replaced with plain words or explained once. Concepts are built up before they are used; results are stated, not revealed. Not a newsletter, not a paper, and not a personal essay.

Reference posts. Explainer: `_drafts/2026-10-20-turning-off-the-neurons-that-make-our-model-say-i-dont-have-that.md`. Launch: `_posts/2026-11-06-introducing-stark-a-local-ai-engine-for-apple-silicon.md`. `_drafts/2026-10-12-testing-subq-snap-on-two-jobs.md` (narrative shape) and `_posts/2026-10-06-testing-openai-decisions-api-as-an-answer-grader.md` (report shape) are earlier explainer registers that are still acceptable for comparison-heavy posts, but new explainer posts should default to the explainer shape. `_drafts/2026-09-20-the-number-i-wasnt-shopping-for.md` is the register we moved away from.

## Voice

- Pick one pronoun per post and keep it. "We" when a team did the work. "I" when one person did, which includes announcements of things the author built alone. Do not mix them: if the post is in "I", then "my earlier posts", "I'll go through", "for myself".
- Declarative and patient. Each paragraph carries one idea, in two to four sentences. Explain the thing before giving the number about it.
- Orient, then deliver. Open a section by saying what it covers or what the reader needs to know, then give the result. The one signpost paragraph after the summary ("In this post I'll go through X, walk through Y, and then cover Z.") is the only place to narrate the post's own structure.
- State claims directly. Do not build suspense or withhold results for a reveal.
- No framing hooks. Do not open with what the post "started as" or "turned into", what it "reminded" you of, what lesson it teaches, or "a question I kept running into" followed by the question. Open with what the thing is and who or what it is for.
- No kicker endings. Do not close on an aphorism, a callback, a turn of phrase, or "the thing I will carry forward". End with what you will do next, or a flat statement of the general point, and stop.
- No performed casualness. No sentence fragments used as paragraph openers ("The numbers.", "Some context.", "One method problem."), no one-line paragraphs used as beats ("Then the catch."), no self-deprecating asides ("this embarrassed me a little"), no "here's the whole thing in one paragraph", no "in case you're building something similar". Say the thing.
- If a sentence would work as the first or last line of a LinkedIn post, cut it.
- Prefer the plain word. "Cut" over "slash", "worse" over "took a hit", "cost" over "bill".
- No rhetorical questions, no puns or metaphors in headings or prose ("prime suspect", "neuron surgery", "closed that door").
- No hedging filler ("I think", "it seems like") unless the uncertainty is real, in which case say what is uncertain and why.
- Understated rather than emphatic. Let the numbers carry the weight. No bold for emphasis inside prose or tables; bold is reserved for lead-in labels in bullet lists (see Formatting).
- Admit mistakes and shortfalls plainly, as facts with numbers. "The dense 27B checkpoint is slower than I want it to be. The most recent run measured 51.48 tokens per second against a target of 70.8." Do not introduce them with a sentence about recording or noting them.
- Past tense for what was done, present tense for what is true.

## Say it, don't announce it

The most common way a draft sounds machine-written is a sentence that announces the next sentence instead of saying something. Delete these on sight. Each row gives the pattern and what to do instead.

| Pattern | Example | Fix |
|---|---|---|
| Worth-sentences | "One target I have not hit is worth recording.", "A few details are worth calling out." | Delete the sentence. Start with the fact. |
| Here-is openers | "Here is what Stark is today.", "Here is what we found." | Delete. Start with the subject: "Stark is a menu bar app..." |
| Placement commentary | "The caveat belongs here rather than at the end.", "This is the part that matters." | Delete. Put the caveat where it belongs and say nothing about having done so. |
| Audience asides | "A short orientation for readers new to this blog." | Delete. Write the orientation paragraph without labelling it. |
| Cleft constructions | "What it does not establish is X.", "The condition that would change the plan is Y." | Uncleft: "It does not establish X.", "Y could change that order." |
| Mirrored closers | "The checks passed; the speed did not.", "Fast where it matters, careful where it counts." | Say the two facts in a plain sentence: "Its checks passed, so the gap is speed, not correctness." |
| Doubled phrases | "a real app for real work", "the right tool for the right job" | Say what it is: "a separate app for work on files". |
| Metaphor for structure | "two front doors", "the gate between chat and editing" | Name the thing: "two interfaces", "without one, a user can chat but cannot have OpenWork edit files". |
| Question as hook | "I built it to answer a question I kept running into: can one tool serve both?" | State the goal: "I built it for two kinds of people at once: ..." |
| Do-and-do-not headings | "Performance and what the numbers do and do not show" | A noun phrase: "Performance". Put the limits in the section body, next to each number. |

A simple test: if a sentence could be deleted and the paragraph would lose no information, delete it. If a sentence's only job is to tell the reader how to feel about the next sentence, delete it.

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

Announcements of things the author built use the Launch register instead; see below.

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
- Unmet targets, stated with the target and the measured number in the same sentence.
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
- Bullets may open with a short bold lead-in label followed by a period ("**Noise floor.** Regenerating the reference moved one verdict out of 376.", "**It checks the Mac first.** Before recommending anything, Guided setup reads unified memory..."). Use this for lists where each item is a distinct named point: method details, design choices, reasons for a decision, failure types, features. Do not use it for lists of rejected variants or plain caveats, and never bold inside running prose.
- Inline code for field names, config keys, and API types (`Choice`, `min_judge_confidence`).
- No emoji. No images unless they carry data a table cannot.

## Launch register

Use this when the post announces something the author built and is releasing: an app, a library, a tool. The reader is anyone who might download it, from a non-technical Mac user to an engineer deciding whether to point their stack at it. The job is to make them want it and tell them exactly what they get, in about two thirds the length an explainer would take. Reference: `_posts/2026-11-06-introducing-stark-a-local-ai-engine-for-apple-silicon.md`.

The launch register is not a different set of facts. It is the same facts, said faster, to the reader instead of about the system.

### Voice

- **Second person throughout.** "your Mac", "the apps you'll actually use", "what you actually want", "You own the decision rule", "you don't need to know what it means to keep going". The reader is in the room.
- **First person singular, with motive.** "I built it for myself to stop choosing." "I want to hear what breaks." The author is a person who made a thing, not a team reporting.
- **Contractions.** "It's", "doesn't", "didn't", "what's", "you'll". Writing them out sounds like the explainer.
- **Confident flat claims, immediately backed.** "Stark is fast." is allowed only because the next sentence is "9.2% faster than MLX-Serve" and "won all six." Never a superlative without a number in the same breath.
- **Benefit before mechanism, mechanism before number.** "The part you'll actually feel is prefix reuse: when OpenWork sends back a 20,000-token conversation, Stark skips the part it has already seen. Follow-ups that took around 8 seconds now take around 1." Feel, then how, then the figure.
- **Short declaratives and deliberate fragments.** Fragments are allowed here as beats, where the explainer bans them: "No Terminal, no API keys, nothing leaves your Mac." "Not one lucky workload; Stark won all six." "No more waiting while the model rereads the whole chat." "So: one engine, one set of models, two interfaces, and a menu item to switch." Use one per paragraph at most, usually as the last line.
- **Everyday images for mechanical things.** "a chat box", "two camps", "plugs it into", "drops you into a chat", "walks you into OpenWork", "speaks the OpenAI API". Concrete and physical, never clever. Still no puns and no extended metaphors.
- **Rounded numbers in the body, exact numbers in the benchmark section.** "around 8 seconds", "20,000-token" in the opening; "7.6–8.6 seconds to 0.6–1.4 seconds" and "245.5" where the numbers live. Rounding must be flagged ("around", "about") and the exact figure must appear somewhere in the post or a linked source.
- **Compressed caveats.** The explainer puts every limit next to its number. The launch register states the number, says the method and raw records are published, and links to them: "The technical page has all three studies and their limits." This is acceptable only when the link actually contains the limits.
- **An ending that asks for something.** Where to get it, where the source is, and an invitation: "Download it at X, the source is on GitHub under MIT, and I want to hear what breaks." No aphorism, no callback, no "this is just the beginning".

### What stays banned

Hype is energy, not noise. All of these still apply:

- No exclamation marks. No "excited", "thrilled", "proud to announce", "game-changer", "blazing", "seamless", "powerful", "supercharge". If a word would appear in a press release, replace it with what the thing does.
- No emoji, no bold in prose, no hashtags.
- No rhetorical questions.
- No announcing sentences. The whole "Say it, don't announce it" table applies. "Here's what's in the rest of the post:" is the one permitted signpost, and it is a colon followed by a list, not a paragraph.
- No claims without numbers. "fast" needs a tok/s or a percentage. "beat every engine" needs the engines named and their figures.
- No softening of unmet targets by omission. If a shortfall is relevant to the reader's decision, it goes in the body with its number. If it is not relevant, it can live in the linked technical page, but the link must exist.
- Headings stay plain noun phrases: "Two audiences, one engine", "What engineers get underneath", "Performance", "What's next". No sentence headings, no headings that perform.

### Shape

1. **Opening paragraph.** What it is in one sentence, in the reader's terms ("runs AI models on your own machine", not "an inference engine"). What it does for them in one or two sentences, naming the apps or workflows they already know. A fragment stating the three biggest absences or guarantees ("No Terminal, no API keys, nothing leaves your Mac."). Who it is for. One sentence saying the post explains how.
2. **`<!--more-->`**.
3. **Why I built it.** Two to four sentences. The problem the author had, what existing tools made them choose between, and that this is the thing they built to stop choosing.
4. **What it is.** One paragraph, every major component named once, in the order a user meets them. Platform requirements in parentheses.
5. **The performance paragraph.** Opens "It's also fast." or equivalent. Two headline comparisons with competitors named, then the one result the reader will feel in daily use, with rounded before/after figures.
6. **Signpost.** One sentence, "Here's what's in the rest of the post:" followed by the section list.
7. **Who it's for.** The audiences, what blocks each today, and the one-sentence design decision that serves both.
8. **The headline workflow.** The thing a new user does first, as a numbered list of three or four steps written as instructions ("click the cat, then Connections, then Apps"). End with the escape hatch for everyone else.
9. **Feature sections**, one per audience, as bold-lead-in bullets of one or two sentences each. Fragments inside bullets are fine ("Unified memory, GPU budget, free storage."). Supported-things lists are one dense paragraph ending with "Not yet:" and the gaps.
10. **Performance.** One or two paragraphs. The clean sweep first with every competitor's number, then the matched-checkpoint comparison, then the peak figure. Second paragraph: records are published, link.
11. **What's next.** One paragraph. The roadmap in one sentence, who decides what comes after, where to download, where the source is, and the invitation.

Total length: roughly 1,200 to 1,500 words. If a section runs past three paragraphs, cut it.

### Explainer to launch, side by side

These are from the same post before and after the pass. Use them to calibrate.

| Explainer | Launch |
|---|---|
| "Stark is a free, open-source Mac app that downloads an open-weight language model, runs it on your Mac's GPU, and makes it available to chat with or to other apps on the same machine." | "Stark is a free, open-source Mac app that runs AI models on your own machine. Pick a model, it downloads it, runs it on your Mac's GPU, and gets it working inside the apps you'll actually use." |
| "Most of my earlier posts are about evaluating small models and decision models such as JevK5 in a training pipeline. Doing that work meant running a lot of local inference on Macs, and the tools I used for it were either comfortable for engineers and opaque to everyone else, or friendly to beginners and slow or limited for engineers." | "I've spent the last few months evaluating small models and decision models like JevK5 on Macs, and every local inference tool I tried made me choose. Either it was built for engineers and baffling to everyone else, or it was friendly and slow." |
| "Performance-wise, on a same-checkpoint comparison with Qwen3.8-Flash-Next on an M5 Max with 128 GB, Stark's maximum observed decode rate was 66.81 tok/s against 61.17 for MLX-Serve, a 9.2% difference." | "It's also fast. Same checkpoint, same Mac, Stark decodes Qwen3.8-Flash-Next 9.2% faster than MLX-Serve." |
| "On supported text paths Stark reuses the unchanged beginning of the previous request. On a synthetic Qwen3-4B 4-bit test with 19,000 to 21,000-token prompts, follow-up prompt processing went from 7.6 to 8.6 seconds without reuse to 0.6 to 1.4 seconds with it." | "The part you'll actually feel is prefix reuse: when OpenWork or OpenCode sends back a 20,000-token conversation for the next turn, Stark skips the part it has already seen. Follow-ups that took around 8 seconds to start now take around 1. No more waiting while the model rereads the whole chat." |
| "A running model by itself is a chat window. Most people want it to read a document, draft a reply, summarize a folder of notes, or edit code, and that takes a separate app that can see files and call tools." | "A model on its own is a chat box. What you actually want is for it to read a document, draft a reply, summarize a folder of notes, or edit your code, and that takes an app that can see files and call tools." |
| "So Stark has one engine, one set of installed models, and two interfaces. Switching between Beginner and Advanced is a menu item." | "So: one engine, one set of models, two interfaces, and a menu item to switch." |
| "**It checks the Mac first.** Before recommending anything, Guided setup reads unified memory, estimates the GPU budget, and checks free storage. The recommendation depends on the result." | "**It checks your Mac first.** Unified memory, GPU budget, free storage. The recommendation depends on what it finds." |
| "The caller owns the decision rule. This is what I use for JevK5 and the app's Decision mode, and it is the reason the engine exists in its current form." | "You own the decision rule. This is what runs JevK5 and the app's Decision mode, and it's why the engine exists." |
| "Embeddings, the Responses API and JSON-schema structured output are not supported." | "Not yet: embeddings, the Responses API, JSON-schema output." |
| "The immediate work is adding reviewed tool-calling templates for more models. ... The condition that would change the plan is feedback from the first group of users." | "More models with reviewed tool-calling templates, more models full stop, and image support beyond Qwen3.5. Past that, the people using it decide." |

The pattern in every row: drop the hedging frame, address the reader, cut the sentence to the clause that carries the fact, and let the number or the concrete noun do the work.

### Front matter for launch posts

Same fields. The title is still descriptive ("Introducing Stark, a Local AI Engine for Apple Silicon"). The description may lead with the biggest win instead of the plainest summary, but it is still one or two sentences with the numbers in them and no exclamation mark.

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
