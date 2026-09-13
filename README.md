# Workshop task: find a sentiment direction in GPT-2 (10 minutes)

**Goal.** Train a linear probe that separates positive from negative sentences
using GPT-2 layer-6 activations. Report held-out accuracy. Then do **one sanity
check** that convinces you the direction is about *sentiment* and not something
else. Use whatever AI tools you normally use, however you normally use them.

**Deliverable.** Not the probe. The filled-in `WORKFLOW_CARD.md`.

## Setup (already done for you)
```bash
uv sync                                   # torch, transformers, sklearn
uv run python data/make_data.py           # writes data/train.json, data/ood.json
```
`extract.py` gives you `activations(texts, layer=6)` -> `[N, 768]` numpy array
and `load_split(path)` -> `(texts, labels)`. GPT-2 runs on CPU in seconds.

## Data
- `data/train.json` — 60 labelled sentences. Split it however you like.
- `data/ood.json` — 16 hand-written sentences. Use it, or don't. Your call.

## What "done" looks like
1. A script or notebook that trains a probe and prints an accuracy.
2. One sanity check and what it told you.
3. `WORKFLOW_CARD.md` filled in. That is what we compare in pairs.

Timebox is strict: 10 minutes. A partial result with an honest card beats a
perfect probe with no card.
