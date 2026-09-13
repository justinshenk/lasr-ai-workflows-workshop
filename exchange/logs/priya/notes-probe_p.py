"""Linear sentiment probe on GPT-2 layer-6 mean-pooled activations, plus two sanity checks.

Risk 1 (negation shortcut): 19/30 train negatives contain "not", 0/30 positives do.
Risk 2 (template/duplicate leakage): random split leaks adjectives and exact duplicates.
"""
import re, numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, GroupKFold
from extract import activations, load_split

LAYER = 6
NEG_WORDS = re.compile(r"\b(not|n't|never|nothing|no)\b", re.I)
has_neg = lambda t: bool(NEG_WORDS.search(t.replace("can't", "can n't").replace("didn't", "did n't").replace("couldn't", "could n't")))

def fit(X, y):
    return LogisticRegression(C=0.1, max_iter=5000).fit(X, y)

def cv_acc(X, y, splits):
    accs = []
    for tr, te in splits:
        accs.append(fit(X[tr], y[tr]).score(X[te], y[te]))
    return np.mean(accs), np.std(accs)

texts, y = load_split("data/train.json")
X = activations(texts, layer=LAYER)
otexts, oy = load_split("data/ood.json")
OX = activations(otexts, layer=LAYER)

# ---- 1. Held-out accuracy, plain random stratified split (5-fold) ----
rand = list(StratifiedKFold(5, shuffle=True, random_state=0).split(X, y))
m, s = cv_acc(X, y, rand)
print(f"[held-out] random 5-fold CV accuracy: {m:.3f} ± {s:.3f}")

# lexical baseline for Risk 1: predict negative iff negation word present
not_rule = np.array([0 if has_neg(t) else 1 for t in texts])
print(f"[baseline] 'not' rule on train: {(not_rule == y).mean():.3f}   (no model needed)")

# ---- Risk 2: leave-adjective-out split, with duplicates removed ----
adj = [t.rstrip(".").split()[-1] for t in texts]           # last word is the adjective
uniq_idx = sorted({t: i for i, t in enumerate(texts)}.values())
print(f"[risk 2] {len(texts) - len(uniq_idx)} exact duplicate sentences in train.json")
Xu, yu, gu = X[uniq_idx], y[uniq_idx], np.array(adj)[uniq_idx]
grp = list(GroupKFold(5).split(Xu, yu, groups=gu))
m2, s2 = cv_acc(Xu, yu, grp)
print(f"[risk 2] dedup + leave-adjective-out 5-fold CV accuracy: {m2:.3f} ± {s2:.3f}")

# ---- Risk 1: negation shortcut, tested on OOD where negation is decorrelated ----
clf = fit(X, y)                                            # final probe on all train
pred = clf.predict(OX)
print(f"[risk 1] OOD accuracy overall: {(pred == oy).mean():.3f}  (n={len(oy)})")
neg_mask = np.array([has_neg(t) for t in otexts])
for name, mk in [("OOD positives WITH negation", (oy == 1) & neg_mask),
                 ("OOD positives w/o negation", (oy == 1) & ~neg_mask),
                 ("OOD negatives (none negated)", oy == 0)]:
    print(f"    {name:32s} acc={(pred[mk] == oy[mk]).mean():.3f}  n={mk.sum()}")
for t, p, g in zip(otexts, pred, oy):
    print(f"      {'ok ' if p == g else 'ERR'} pred={p} gold={g}  {t}")

# counterfactual: does the probe treat "not <negative adj>" as more negative than "<negative adj>"?
cf = ["The film was awful.", "The film was not awful.",
      "The film was great.", "The film was not great."]
logit = activations(cf, layer=LAYER) @ clf.coef_[0] + clf.intercept_[0]
print("[risk 1] probe logit (>0 = positive):")
for t, l in zip(cf, logit):
    print(f"      {l:+.2f}  {t}")
