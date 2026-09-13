import numpy as np
from extract import activations, load_split

for split in ("train", "ood"):
    texts, y = load_split(f"data/{split}.json")
    X = activations(texts, layer=6)
    np.save(f"{split}_X.npy", X)
    np.save(f"{split}_y.npy", y)
    print(split, X.shape, y.shape)
