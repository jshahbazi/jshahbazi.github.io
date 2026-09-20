---
layout: post
title: "The Before Column"
description: "How differences in starting accuracy made a training-data effect look convincing, and what retention and recovery revealed."
---

I thought I'd figured out why our second training stage was making a model forget facts. Several cuts of the data agreed, the explanation made sense, and it pointed to a fairly straightforward fix. Then I looked more carefully at the column showing where each group started.

<!--more-->

We train small models on document collections. The first stage teaches the facts. The second teaches things like refusing questions the documents can't answer and pushing back on false premises. In this run, accuracy on fresh questions fell from about 58% to 43% after the second stage.

Fifteen points is a lot to lose. We'd also just tried changing the composition of the training data, with no measurable improvement. I wanted to understand whether we'd picked the wrong change.

So I grouped facts by how many examples in the second stage taught the model to answer them correctly, then compared accuracy before and after.

| Supporting examples per fact | Before | After | Change |
|---|---:|---:|---:|
| 1–9 | 66.4% | 47.5% | −18.9 points |
| 10–29 | 59.2% | 44.5% | −14.7 points |
| 30 or more | 52.3% | 39.2% | −13.1 points |

That's a pretty convincing table. More supporting examples, less damage. Every bucket moves in the expected direction.

Other cuts agreed. Facts with more refusal examples lost more accuracy. Facts that had received extra examples during a repair pass lost less. I could already see the next experiment: rebalance the examples and check whether recall held up.

But look at the before column. Every group that lost more also started higher.

A group starting at 66% has more correct answers available to lose than a group starting at 52%. It also has fewer wrong answers available to fix. Both affect the change score.

Here's a small example. Say a training stage keeps 60% of previously correct answers and fixes 20% of previously wrong ones. Apply those same rates to two groups of 100 questions:

- A group starting with 80 correct keeps 48 and gains 4. It finishes at 52, down 28 points.
- A group starting with 40 correct keeps 24 and gains 12. It finishes at 36, down 4 points.

Same retention. Same recovery. A 24-point difference in apparent damage.

Whatever property you used to define those groups can now look like an explanation for that difference. You don't need measurement noise to produce it. Those transitions could happen in a completely deterministic system.

The arithmetic fits on two lines. If starting accuracy is `A`, retention is `r`, and recovery is `g`:

```text
after  = A*r + (1-A)*g
change = g - A*(1+g-r)
```

With fixed retention and recovery rates, higher starting accuracy produces a larger expected drop. The statistical term is mathematical coupling: the starting value is part of the change you're trying to explain.

I reran the analysis using the transitions directly. Of the questions the first checkpoint got right, how many did the final model keep right? Of the ones it got wrong, how many did it fix?

The supporting-example groups retained 61.5%, 58.9%, and 57.0%, respectively. The apparent protective effect disappeared. The direction even flipped, though the differences weren't statistically significant. The repaired and unrepaired facts retained 58.7% and 59.1%. Almost identical.

Using the overall retention and recovery rates, a model with just those two parameters reproduced the original bucket changes to within about a point and a half. The groups' starting accuracies explained most of what had looked like a training-data effect.

That still leaves room for smaller effects. This analysis couldn't establish that adding examples never helps. It did take away the evidence I was about to use to justify doing it.

Question form remained worth investigating. Among initially correct answers, the model retained about 67% on who/what/where-style questions and 50% on yes/no questions. That difference survived the same analysis. We'd already suspected it because of an imbalance in the training data.

The annoying part is that we had a warning about this general problem in our research notes. It covered groups selected by their outcomes. I'd grouped by training inputs, so I didn't think the warning applied. It needed to say what to check: groups with different starting accuracies have different opportunities to gain and lose.

I also gave too much weight to several cuts agreeing. They all used the same change score, and all carried the same baseline problem. Each extra table made me more confident without adding much evidence.

For the next analysis, I want the counts of answers kept, lost, and recovered alongside the overall score. They're cheap to compute from the same results. In this case, they would have saved me from planning another training run around a pattern I could reproduce with two probabilities and a subtraction.
