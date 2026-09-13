"""Linear sentiment probe on GPT-2 layer-6 mean-pooled activations.

Held-out accuracy: leave-one-out CV over deduplicated data/train.json
(60 rows -> 55 unique sentences).  Sanity check: the training negatives are
mostly "X was not ADJ" (19/30 use "not", 0/30 positives do), so the obvious
confound is a "contains not" detector.  We test that three ways:
  1. data/ood.json: 5 of its 8 positives contain negation words.
  2. Train only on sentences containing "not" (all negatives) + all positives,
     test on the 11 lexical negatives (dull, terrible, ...) that have no "not".
  3. Counterfactual "The film was not dull." style sentences (not + neg adj),
     which a "not"-detector calls negative and a sentiment probe calls positive.
"""
import re
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from extract import activations, load_split

RNG = 0
NEG_RE = re.compile(r"\b(not|n't|never|nothing)\b", re.I)


def probe():
    return make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000))


def acc(y, p):
    return float((np.asarray(y) == np.asarray(p)).mean())


# ---- data ----------------------------------------------------------------
texts, labels = load_split("data/train.json")
uniq = {}
for t, l in zip(texts, labels):
    uniq.setdefault(t, l)
texts, labels = list(uniq), np.array(list(uniq.values()))
print(f"train: {len(texts)} unique sentences (from 60 rows), "
      f"{labels.sum()} pos / {(labels == 0).sum()} neg")
X = activations(texts, layer=6)

# ---- held-out accuracy: leave-one-out -----------------------------------
pred = cross_val_predict(probe(), X, labels, cv=LeaveOneOut())
print(f"\n[1] LOO held-out accuracy on train.json: {acc(labels, pred):.3f} "
      f"({(labels == pred).sum()}/{len(labels)})")
for t, l, p in zip(texts, labels, pred):
    if l != p:
        print(f"    miss: {t!r}  true={l} pred={p}")

# also a plain 70/30 stratified split, single seed, for reference
from sklearn.model_selection import train_test_split
tr, te = train_test_split(np.arange(len(texts)), test_size=0.3,
                          stratify=labels, random_state=RNG)
clf = probe().fit(X[tr], labels[tr])
print(f"    70/30 split ({len(te)} test): {acc(labels[te], clf.predict(X[te])):.3f}")

# baseline the number must beat: "contains a negation word" -> negative
neg_rule = np.array([0 if NEG_RE.search(t) else 1 for t in texts])
print(f"    'not'-rule baseline on train.json: {acc(labels, neg_rule):.3f}")

# ---- final probe on all train data --------------------------------------
clf = probe().fit(X, labels)

# ---- sanity check A: OOD set, esp. positives that contain negation -------
ood_texts, ood_labels = load_split("data/ood.json")
ood_pred = clf.predict(activations(ood_texts, layer=6))
print(f"\n[2] OOD accuracy: {acc(ood_labels, ood_pred):.3f} "
      f"({(ood_labels == ood_pred).sum()}/{len(ood_labels)})")
print(f"    'not'-rule baseline on OOD: {acc(ood_labels, [0 if NEG_RE.search(t) else 1 for t in ood_texts]):.3f}")
for t, l, p in zip(ood_texts, ood_labels, ood_pred):
    flag = "NEGWORD" if NEG_RE.search(t) else "       "
    print(f"    {'ok  ' if l == p else 'MISS'} {flag} true={l} pred={p}  {t}")

# ---- sanity check B: hold out every negative that lacks "not" ------------
has_not = np.array([bool(re.search(r"\bnot\b", t)) for t in texts])
lex_neg = (labels == 0) & ~has_not          # dull, terrible, dreadful, ...
keep = ~lex_neg
clf_b = probe().fit(X[keep], labels[keep])  # negatives seen = ONLY "not" ones
pb = clf_b.predict(X[lex_neg])
print(f"\n[3] Train with negatives = only 'not' sentences; test on the "
      f"{lex_neg.sum()} lexical negatives (no 'not'):")
print(f"    accuracy: {acc(labels[lex_neg], pb):.3f}  "
      f"(a 'not'-detector would score 0.0)")
for t, p in zip(np.array(texts)[lex_neg], pb):
    print(f"    {'ok  ' if p == 0 else 'MISS'} pred={p}  {t}")

# ---- sanity check C: counterfactual "not + negative adjective" -----------
cf = ["The film was not dull.", "The trip was not terrible.",
      "The service was not dreadful.", "The meal was not disappointing.",
      "The party was not boring.", "The flight was not unpleasant."]
pc = clf.predict(activations(cf, layer=6))
print(f"\n[4] 'not + negative adjective' counterfactuals (a sentiment probe "
      f"should lean positive, a 'not'-detector says 0):")
for t, p in zip(cf, pc):
    print(f"    pred={p}  {t}")
print(f"    fraction called positive: {pc.mean():.2f}")

# ---- control: shuffled labels, LOO, 10 permutations ----------------------
rng = np.random.default_rng(RNG)
shuf = [acc(y, cross_val_predict(probe(), X, y, cv=LeaveOneOut()))
        for y in (rng.permutation(labels) for _ in range(10))]
print(f"\n[5] shuffled-label LOO accuracy (10 perms): mean={np.mean(shuf):.3f} "
      f"max={np.max(shuf):.3f}  (real: {acc(labels, pred):.3f})")
