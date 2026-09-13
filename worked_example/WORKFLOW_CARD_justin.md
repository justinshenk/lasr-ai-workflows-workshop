# Workflow card — Justin (the worked example)

Name: Justin   Tool(s): Claude Code (Fable 5.1) in the terminal   Familiarity with probing (1-5): 3

## 1. What I asked the AI to do, roughly in order
1. "Check what's installed; can we run GPT-2 locally?" (env check, ~1 min)
2. "Write a helper that returns mean-pooled layer-6 GPT-2 activations for a list of sentences." (extract.py)
3. "Generate a small sentiment dataset for training a probe." (data/make_data.py — I told it to make it templated, because that's what an AI-generated dataset usually looks like)
4. "Train a logistic-regression probe, report held-out accuracy." → 1.00
5. "Now add sanity checks: OOD set, shuffled labels, and check whether it's really a negation detector."

## 2. What I did myself vs. what I delegated
- Me: chose layer 6, chose mean pooling, decided the task, wrote the 16 OOD sentences by hand, chose which sanity checks to run.
- AI: all the sklearn/torch plumbing, the batching, the dataset generator, the printing.
- Split was roughly 20% me / 80% AI by lines, 70% me / 30% AI by decisions.

## 3. What I checked before believing the number
- Held-out accuracy on a random split: 1.00. Looked great.
- OOD accuracy on hand-written sentences: 0.56. That is chance for 16 items.
- Shuffled-label control: mean 0.49, max 0.72 over 20 runs. So 1.00 wasn't overfitting noise; the probe learned something real about the *training distribution*, just not sentiment.
- Which OOD items fail: every hand-written POSITIVE is predicted negative. Negatives are fine.

## 4. Where the AI led me astray, or would have if I hadn't looked
- The first number (1.00) is exactly the kind of result you paste into a Slack update. It is meaningless: train and test share templates.
- My own hypothesis was also wrong. I predicted a *negation* confound (I built the dataset with 63% of negatives using "not"). The data said the probe is a *template* detector: "The X was [nice adj]." → positive, anything else → negative. Predicted-negative rate on OOD sentences *without* negation was 0.92. I would have written "negation confound" in the writeup if I hadn't printed the per-item failures.
- The AI did not volunteer any of the checks. It ran the check I asked for and reported it neutrally. Sanity checks came from me, not from it.

## 5. One thing from this run I would reuse next time
A `/sanity-check` prompt I keep in the repo: "Before reporting an accuracy: (a) evaluate on data from a different generating process, (b) shuffled-label control, (c) print the individual failures, (d) state the simplest non-target feature that could explain the score." Costs 2 minutes; would have saved a wrong claim here.

## 6. One thing I'd like to steal from someone else
(To be filled in the pair review. My guess: someone will have had the AI generate the OOD set too, and I want to see whether that catches the confound or shares it.)
