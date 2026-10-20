SubQ Snap is a hosted decision model: you send it context, instructions, and a fixed set of options, and it returns one option plus a probability for each. Same interface as TypeSafe's Jev, the open JevK5 models, and OpenAI's Decisions API. I ran it through two jobs. It was the best tool picker we have measured and a middling answer grader.

The tool test is a public 250-case set where an agent sees a request and a handful of tool descriptions and has to pick the right tool, or say none applies. Snap got all 250 right under the dataset's scoring rules: every applicable tool chosen, zero unnecessary tool calls on the 50 cases with no fit. Median response time was 155ms and the whole experiment cost under a cent. JevK5-9B was next at 98.8%, which is three judgments behind, so the margin is small, but nothing else had a clean sheet.

The grading test is the same 100 hand-graded answers every grader on this blog has seen, run with and without the source document. Snap agreed with the human labels 84% and 86% of the time. JevK5-4B, our local grader, scored 90% and 88% on identical requests. Both let the same number of bad answers through; Snap's gap comes from rejecting more good ones, 8 of 67 versus 2.

My guess at why is that the two jobs ask for different things. Picking a tool from a short list is mostly matching. Grading means noticing that "30 days after purchase" is not "30 days after delivery" in an answer that is otherwise fluent and on topic. The typed interface does not do that part for the model.

It is cheap enough that the question barely matters for experimentation: both tests together came to about 3.6 cents at $0.05 per million input tokens. Snap goes in as the hosted candidate for our next tool-selection work. For grading, I am staying with JevK5-4B.

Full writeup, with the tables and caveats: https://johnshahbazian.com/testing-subq-snap-on-two-jobs
