"""Linear probe for sentiment on GPT-2 layer-6 mean-pooled activations.

Usage: HF_HUB_OFFLINE=1 uv run python probe_q.py
"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from extract import activations, load_split

LAYER = 6
SEED = 0

texts, y = load_split("data/train.json")
X = activations(texts, layer=LAYER)

# train.json has duplicate sentences; group by text so none straddle the split.
groups = np.unique(texts, return_inverse=True)[1]
tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=SEED).split(X, y, groups))

probe = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=2000))
probe.fit(X[tr], y[tr])

print(f"layer {LAYER} | train n={len(tr)} test n={len(te)}")
print(f"train accuracy:    {probe.score(X[tr], y[tr]):.3f}")
print(f"held-out accuracy: {probe.score(X[te], y[te]):.3f}")

# Extra: the hand-written OOD set, where negation is decorrelated from sentiment.
ood_texts, ood_y = load_split("data/ood.json")
print(f"ood accuracy:      {probe.score(activations(ood_texts, layer=LAYER), ood_y):.3f}  (n={len(ood_y)})")
