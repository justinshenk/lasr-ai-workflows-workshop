"""Worked example: the naive run, then the sanity checks. Run: uv run python probe.py"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from extract import activations, load_split

LAYER = 6
texts, y = load_split("data/train.json")
X = activations(texts, layer=LAYER)

# --- Step 1: the naive thing. Held-out accuracy on a random split. ---
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
clf = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
print(f"[1] held-out acc (random split of train.json): {clf.score(Xte, yte):.2f}")

# --- Step 2: sanity check A. Does the direction transfer to hand-written sentences? ---
ood_t, ood_y = load_split("data/ood.json")
Xo = activations(ood_t, layer=LAYER)
print(f"[2] OOD acc (data/ood.json):                    {clf.score(Xo, ood_y):.2f}")

# --- Step 3: sanity check B. My hypothesis: the probe is a negation detector. (Spoiler: the data disagreed.) ---
has_neg = np.array([("not" in t.split() or "n't" in t) for t in ood_t])
pred = clf.predict(Xo)
print(f"[3] on OOD, P(pred=negative | negation present)  = {(pred[has_neg]==0).mean():.2f}  (n={has_neg.sum()})")
print(f"    on OOD, P(pred=negative | no negation)       = {(pred[~has_neg]==0).mean():.2f}  (n={(~has_neg).sum()})")
neg_frac_train = np.mean([("not" in t.split()) for t, l in zip(texts, y) if l == 0])
print(f"    in train.json, fraction of NEGATIVE examples containing 'not': {neg_frac_train:.2f}; of POSITIVE: 0.00")

# --- Step 4: sanity check C. Shuffled-label control (what does 'chance' look like at 768-d, n=42?) ---
rng = np.random.default_rng(0)
accs = [LogisticRegression(max_iter=2000).fit(Xtr, rng.permutation(ytr)).score(Xte, yte) for _ in range(20)]
print(f"[4] shuffled-label held-out acc: mean {np.mean(accs):.2f}, max {np.max(accs):.2f}")

# --- Step 5: the fix. Train on de-confounded data (negation-free negatives + OOD), test on the rest. ---
print("[5] which OOD sentences does the naive probe get wrong?")
for t, l, p in zip(ood_t, ood_y, pred):
    if l != p: print(f"      true={'pos' if l else 'neg'} pred={'pos' if p else 'neg'}  {t}")
