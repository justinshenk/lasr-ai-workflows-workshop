# Annotated session — what fellows would watch me do live (~8 min)

Everything below actually ran. Output is in `run_output.txt`. Code in `../probe.py`.

**[0:00] Ask.** "Train a linear probe for sentiment on GPT-2 layer-6 activations, report held-out accuracy."
Claude writes `probe.py` steps 1 in ~30s. Runs.
> `[1] held-out acc (random split of train.json): 1.00`

**[1:00] Pause and ask the room.** "Would you put this in your team's update?" Most people say
"well, I'd want more data" but nobody says the number is *meaningless*. It is.

**[1:30] Check A: different generating process.** I hand-wrote 16 sentences (`data/ood.json`).
> `[2] OOD acc: 0.56`
Chance. The direction does not transfer.

**[2:30] Check B: my hypothesis.** I built the training data with 63% of negatives as "not + positive adj",
so I *expected* a negation detector. I asked Claude to test that.
> `P(pred=negative | negation present) = 1.00 (n=3)`
> `P(pred=negative | no negation)      = 0.92 (n=13)`
The second line kills my hypothesis. It predicts negative for almost everything hand-written.

**[4:00] Check C: shuffled labels.** Rules out "1.00 is just 768 dims fitting 42 points."
> `shuffled-label held-out acc: mean 0.49, max 0.72`
So it genuinely learned *something* in-distribution.

**[5:00] Check D: look at the failures.** Every hand-written positive → predicted negative. Every negative correct.
Conclusion: the probe learned "matches the positive template" vs "doesn't". A style detector, not a sentiment direction.

**[6:30] The point.** Three things to notice:
1. The AI did nothing wrong. Every line of code is correct. The *experiment design* was wrong, and the AI executed it faithfully.
2. Neither the AI nor I predicted the actual failure. Only the check found it. That is what "systematic" buys you over "skilled but improvised."
3. Each check was two lines. Total cost: ~3 minutes. The cost of *not* doing it is a week believing a wrong result.

**[7:30] Hand-off to the exercise.** "You have 10 minutes. Same task, your tools, your habits. Fill in the card as you go, not after."
