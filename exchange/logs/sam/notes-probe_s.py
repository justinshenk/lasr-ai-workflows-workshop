"""Linear sentiment probe on GPT-2 layer-6 mean-pooled activations, plus
adversarial checks on whether the score is really about sentiment."""
import json, re, numpy as np
from collections import Counter
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, GroupKFold
from extract import activations, load_split

LAYER = 6
def probe(): return LogisticRegression(C=1.0, max_iter=5000)
def has_not(t): return bool(re.search(r"\bnot\b|n't\b|\bnever\b|\bnothing\b", t.lower()))

texts, y = load_split("data/train.json")
X = activations(texts, layer=LAYER)
print(f"train: {len(texts)} rows, {Counter(y.tolist())}, unique texts={len(set(texts))}")

# ---------- 1. held-out accuracy (stratified 5-fold, plus a fixed 40/20 split) ----------
rng = np.random.RandomState(0)
cv = StratifiedKFold(5, shuffle=True, random_state=0)
accs = []
for tr, te in cv.split(X, y):
    accs.append((probe().fit(X[tr], y[tr]).predict(X[te]) == y[te]).mean())
print(f"\n[1] 5-fold CV accuracy: {np.mean(accs):.3f} (folds {np.round(accs,2)})")

# duplicates leak across random folds -> group by text so identical sentences stay together
groups = [hash(t) for t in texts]
g_accs = []
for tr, te in GroupKFold(5).split(X, y, groups):
    g_accs.append((probe().fit(X[tr], y[tr]).predict(X[te]) == y[te]).mean())
print(f"    grouped-by-text 5-fold: {np.mean(g_accs):.3f}  (dupes: {sum(c-1 for c in Counter(texts).values())} repeated rows)")

# ---------- 2. boring baselines that use no activations at all ----------
not_pred = np.array([0 if has_not(t) else 1 for t in texts])
len_pred = np.array([0 if len(t.split()) > 4 else 1 for t in texts])
print(f"\n[2] no-model baselines on train:")
print(f"    'not' in sentence -> negative : {(not_pred==y).mean():.3f}")
print(f"    >4 words -> negative           : {(len_pred==y).mean():.3f}")
print(f"    negation by label: {Counter((has_not(t), int(l)) for t,l in zip(texts,y))}")

# ---------- 3. is the probe a negation detector? ----------
# 3a. train on negated negatives only (+ positives), test on lexical negatives (awful/dull/...)
neg_lex = np.array([l==0 and not has_not(t) for t,l in zip(texts,y)])
neg_not = np.array([l==0 and has_not(t) for t,l in zip(texts,y)])
pos = y==1
tr = pos | neg_not
clf = probe().fit(X[tr], y[tr])
print(f"\n[3a] train on positives + negated negatives; test on {neg_lex.sum()} lexical negatives:")
print(f"     accuracy on lexical negatives: {(clf.predict(X[neg_lex])==0).mean():.3f}")

# 3b. reverse: train on positives + lexical negatives, test on negated negatives
tr = pos | neg_lex
clf = probe().fit(X[tr], y[tr])
print(f"[3b] train on positives + lexical negatives; test on {neg_not.sum()} negated negatives:")
print(f"     accuracy on negated negatives: {(clf.predict(X[neg_not])==0).mean():.3f}")

# 3c. how similar is the full-data sentiment direction to a 'contains not' direction?
full = probe().fit(X, y)
notclf = probe().fit(X, np.array([has_not(t) for t in texts]).astype(int))
w1, w2 = full.coef_[0], notclf.coef_[0]
print(f"[3c] cos(sentiment weights, negation weights) = {np.dot(w1,w2)/np.linalg.norm(w1)/np.linalg.norm(w2):.3f}")
print(f"     probe trained to detect 'not' from activations, 5-fold acc: "
      f"{np.mean([(probe().fit(X[a], np.array([has_not(t) for t in texts])[a]).predict(X[b])==np.array([has_not(t) for t in texts])[b]).mean() for a,b in cv.split(X,y)]):.3f}")

# 3d. counterfactuals: same template, negation flipped against sentiment
NOUNS = ["film","meal","hotel","book","trip"]
POS = ["wonderful","excellent","lovely","great","fantastic"]
NEG = ["awful","terrible","boring","dull","poor"]
cf_texts, cf_y, kind = [], [], []
for n,p,q in zip(NOUNS,POS,NEG):
    cf_texts += [f"The {n} was not {q}.", f"The {n} was {q}.", f"The {n} was {p}.", f"The {n} was not {p}."]
    cf_y     += [1, 0, 1, 0]
    kind     += ["not+NEG(=pos)", "NEG", "POS", "not+POS(=neg)"]
cf_pred = full.predict(activations(cf_texts, layer=LAYER))
print(f"\n[3d] counterfactual templates (full-data probe):")
for k in ["POS","not+POS(=neg)","NEG","not+NEG(=pos)"]:
    m = np.array([kk==k for kk in kind])
    print(f"     {k:16s} acc {(cf_pred[m]==np.array(cf_y)[m]).mean():.2f}   preds {cf_pred[m].tolist()}")

# ---------- 4. OOD set: negation decorrelated from sentiment ----------
ot, oy = load_split("data/ood.json")
op = full.predict(activations(ot, layer=LAYER))
print(f"\n[4] ood.json ({len(ot)} rows): accuracy {(op==oy).mean():.3f}")
print(f"    pos w/ negation words -> predicted: {[int(p) for t,p,l in zip(ot,op,oy) if l==1 and has_not(t)]}")
print(f"    pos w/o negation      -> predicted: {[int(p) for t,p,l in zip(ot,op,oy) if l==1 and not has_not(t)]}")
print(f"    neg (no negation)     -> predicted: {[int(p) for t,p,l in zip(ot,op,oy) if l==0]}")
