Six cents. That is what it cost to have OpenAI's new Decisions API grade 400 answers, and each one came back in roughly 135ms including the network. It also marked three times as many correct answers wrong as the graders we already use. Both facts matter, and the second one is why we are not switching.

Some context. We train small models on customer documents and grade their answers as part of every eval. For the past month I have been testing cheap, fast "decision" services as a stand-in for having Claude do that grading: TypeSafe's Jev first, then a set of open models that copy its interface. OpenAI's Decisions API is the newest entrant. It is a separate endpoint that takes an input and a typed question (true/false, pick one of your options, or rate on a scale) and returns a decision with probabilities. No generated text, no explanation, billed on input tokens only at $0.10 per million.

We gave it the same 100 hand-graded answers every other grader has seen: 67 a person accepted, 33 a person rejected, each run twice, once with and once without the source document. Without the source it agreed with the human labels 83% of the time. On the same cases Jev scored 90% and JevK5-4B, the open model we picked last time, scored 89%.

The totals hide the useful part. On bad answers, OpenAI and JevK5-4B were tied: each let 8 of the 33 through. On good answers they were not. OpenAI rejected 9 of 67 where JevK5-4B rejected 3, and handing it the source text pushed that to 11. A strict grader that also caught more bad answers would be a fair trade. This one is stricter without being more discerning, and in an eval pipeline that means a model can look worse than it is.

The caveats are real. 100 cases is enough to see which way the errors lean but not to settle a six-point gap; the 95% interval against JevK5-4B crosses zero. The service is in public beta with a single unpinned model, gpt-6-luna, so a rerun next month may not reproduce these numbers. It does return a confidence score, which we logged but have not yet tested as a hand-off trigger the way we did with Jev.

Where this leaves us: Jev hosted, JevK5-4B locally, production untouched. The speed and price are hard to argue with. Long-input requests came back in about one-seventh of JevK5-4B's local time, and the ~2,350 answers that cost about $43.60 to grade with Opus would run about $0.65 here. If a later version brings the false rejects down, it goes back on the list.

Full writeup, with the tables and caveats: https://jshahbazi.github.io/testing-openai-decisions-api-as-an-answer-grader
