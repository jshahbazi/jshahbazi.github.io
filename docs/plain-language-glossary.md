# Plain-language glossary

A reference for adjusting register depending on the audience. Left column is how I'd say it to someone in ML/evals; right column is how to say the same thing to an experienced engineer who doesn't live in that world. The point is not that the jargon is wrong. It's that each term costs the reader a lookup, and the budget for lookups is small.

Rule of thumb: if a term names a *concept* the reader already has under a different name, translate it. If it names a concept they don't have at all, keep the term and define it once inline.

## From the Jev post

These are the substitutions made when rewriting the Jev draft for a general audience.

| Specialist | Plain | Notes |
|---|---|---|
| frontier model | large commercial model (Claude, GPT) | Name the actual model if you can. |
| fine-tune | train (on our documents) | "Fine-tune" is fine for ML-adjacent readers; "train" loses a nuance but nobody misreads it. |
| 8×A100 hour | an hour on an 8-GPU machine | The GPU model number means nothing to most people. |
| GPU-hours | hours of GPU time / GPU cost | |
| non-autoregressive classification model | a model that answers structured questions instead of generating text | Describe what it *does*, not how it's built. |
| state blob | a chunk of data / the input | |
| typed questions / typed answers | questions with fixed answer types | |
| output tokens / input tokens | what the model writes / what you send it | Keep "tokens" when quoting pricing; explain once. |
| latency | response time | |
| fail closed | default to the safe/negative answer | Engineers know "fail closed," but "default to `incorrect`" is clearer in context. |
| hand-labelled / gold labels / ground truth | graded by hand / what a person said the answer was | |
| human-label agreement | how often the grader agrees with the human | |
| n=200 | 200 judgments | Just say the number and what it counts. |
| arm | variant / configuration / version | Experiment-design jargon. Almost nobody outside research uses it. |
| condition | setup / scenario | As in "the no-evidence condition." |
| source evidence | the source document / the original text | "Evidence" sounds legal. |
| condenser | filter | Name the thing by what it does. |
| dilution | too much irrelevant text | |
| token overlap | shared words | |
| fan-out | ask about every item at once | |
| pre-registered | wrote down the target before running | Say what you did, not the methodology term for it. |
| partial recovery | partially fixed | |
| within noise / not significant | too close to tell apart | |
| failure analysis | looking at why it failed | |
| decisive case | key example | |
| verbatim | word for word | |
| retention | kept | As in "the filter kept 87.5% of the terms." |
| inferential step | reasoning step | |
| adjacent provision | the paragraph next door / the neighboring section | |
| methodological error | a mistake in how I ran the test | |
| arbiter / adjudicate | tiebreaker / settle the disagreement | |
| blind | without telling it which side said what | |
| model family | vendor | Slightly lossy (a vendor can have several families) but right 95% of the time. |
| report the intersection | only count rows where both agree | |
| calibrated / calibration | the confidence means what it says; when it says 90% it's right about 90% of the time | Always define this one. It's the concept most worth teaching. |
| monotonically | steadily / consistently in one direction | |
| bin / binning | bucket / grouping | |
| gate / gating | threshold / cutoff | |
| triage | decide which ones a human should look at | |
| contested rows | the disputed ones / the hard cases | |
| router / routing | first-pass filter / deciding which cases go where | |
| cascade | two-stage setup | |
| escalate | send to the more expensive model / hand off | |
| false accept / false positive | wrong answer marked correct | Spell it out. People mix up which direction FP/FN means. |
| false reject / false negative | right answer marked wrong | |
| conditioned on X | based on X / using X as input | |
| fixed artifact | doesn't change / fixed | |
| post hoc | after the fact | |
| circular | tested on the same data I used to pick the settings | Describe the circularity rather than naming it. |
| held-out set | a separate set of cases not used for tuning | |
| recall questions | straightforward fact-recall questions | |
| adversarial probes | trick questions designed to catch the model | |
| oracle | if you could magically pick the best option every time | |
| headroom | room for improvement | |
| cost lever, not an accuracy lever | saves money; doesn't improve accuracy | |
| validate | test on fresh data | |

## Other ML / evals terms worth translating

| Specialist | Plain | Notes |
|---|---|---|
| inference | running the model / getting an answer from the model | Do not assume people know this means "using" and not "training." |
| checkpoint | a saved version of the model partway through training | |
| epoch | one full pass over the training data | |
| loss | the training error score / how wrong the model is | |
| overfit | memorized the training data instead of learning the pattern | |
| generalize | works on data it hasn't seen | |
| distribution shift / out of distribution | the real data looks different from what it was trained on | |
| hallucination | made something up / stated a false fact confidently | |
| grounding / grounded | backed by the source document | |
| RAG | look up relevant documents, then paste them into the prompt | Define once; the acronym itself is fine after that. |
| context window | how much text the model can take in at once | |
| prompt | the instructions and input you send | |
| few-shot / zero-shot | with examples in the prompt / with no examples | |
| temperature | randomness setting | |
| sampling | picking the next word (with some randomness) | |
| greedy decoding | always pick the most likely next word | |
| logits / logprobs | the model's raw scores / probabilities for each option | |
| softmax | turn scores into probabilities that add to 1 | |
| embedding | a numeric fingerprint of the text so you can compare meanings | |
| vector similarity / cosine similarity | how close two of those fingerprints are | |
| LLM-as-judge | using a model to grade another model's answers | |
| rubric | the grading criteria | Actually fine for most readers. |
| eval / eval set / benchmark | test / test set / standard test | |
| harness | the code that runs the test and collects results | |
| ablation | removing one piece to see how much it mattered | |
| baseline | the thing you're comparing against / the current setup | |
| SOTA | the best published result | |
| regression | got worse than before | Note: means something different in ML (fitting a line) vs. engineering (a bug that came back). Clarify. |
| precision / recall | of the ones it flagged, how many were right / of the real ones, how many did it catch | Always spell out. Even ML people mix them up. |
| F1 | a single score that balances precision and recall | |
| AUC / ROC | how well it separates the two classes across every threshold | Usually just say "how well it separates the classes." |
| confusion matrix | a table of right vs. wrong by category | |
| class imbalance | far more of one kind of case than the other | |
| stratified | split so each group is represented proportionally | |
| confidence interval | the range the true number is probably in | |
| p-value / statistically significant | unlikely to be chance | Just say the plain version; the p-value adds little for most readers. |
| variance | how much the results bounce around between runs | |
| seed | the random starting point, fixed so runs are repeatable | |
| deterministic | same input, same output every time | |
| quantization | shrinking the model by using lower-precision numbers | |
| distillation | training a small model to imitate a big one | |
| LoRA / adapter | a small trainable add-on so you don't retrain the whole model | |
| alignment / RLHF | training the model to behave the way people want | |
| agent | a model that takes actions in a loop, not just answers once | |
| tool use / function calling | letting the model call your code | |

## General register shifts

Not term-for-term; these are patterns.

| Instead of | Try | Why |
|---|---|---|
| Naming the methodology ("pre-registered," "blind," "held-out") | Describing what you did ("wrote the target down first," "didn't tell it which side," "used cases I hadn't tuned on") | The name is a compression that only works if the reader already has the concept. |
| Latin and Greek ("post hoc," "a priori," "monotonic," "orthogonal") | English ("after the fact," "before looking," "steadily," "unrelated / independent") | |
| Nominalizations ("retention," "adjudication," "condensation") | Verbs ("kept," "settled," "shortened") | Verbs are easier to parse and harder to misread. |
| Acronyms on first use | The expanded phrase, then the acronym in parentheses if you'll reuse it | |
| "X is a Y lever" | "X changes Y" / "X saves money but doesn't improve accuracy" | |
| "the model exhibits..." / "we observe..." | "the model does..." / "I saw..." | Passive-academic voice. Fine in a paper, deadening in a post. |
| Precise-sounding hedges ("suggests," "is consistent with") | Plain hedges ("probably," "looks like," "I think") | The academic hedge sounds more rigorous but communicates less. Say how sure you are. |
| Percent points vs. percent | Spell out when it matters: "0.5 points is one judgment in 200" | People conflate "dropped 0.5%" with "dropped 0.5 points." Give the count. |
| Numbers alone | Numbers plus what they count | "n=100" → "100 cases." "89.0%" → "89.0% agreement with the human grader." |

## When *not* to translate

- The audience is the specialist audience. Translating for them reads as condescending and costs precision.
- The term is the thing you're teaching. Define it, use it, and let the reader acquire it. ("Calibrated" in the Jev post is a candidate for this.)
- The plain version is genuinely ambiguous. "Filter" is fine for a condenser; "test" for "eval" can collide with unit tests in an engineering context, so sometimes "eval" is the clearer word.
- Code identifiers, API names, config keys. Never paraphrase those. `min_judge_confidence` stays `min_judge_confidence`.
