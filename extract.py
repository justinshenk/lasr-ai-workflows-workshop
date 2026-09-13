"""Helper: mean-pooled GPT-2 hidden states at a given layer. Runs on CPU/MPS in seconds."""
import json, torch, numpy as np
from transformers import AutoTokenizer, AutoModel

_tok = _model = None

def load():
    global _tok, _model
    if _model is None:
        _tok = AutoTokenizer.from_pretrained("gpt2")
        _tok.pad_token = _tok.eos_token
        _model = AutoModel.from_pretrained("gpt2", output_hidden_states=True).eval()
    return _tok, _model

def activations(texts, layer=6, pool="mean"):
    tok, model = load()
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), 16):
            batch = tok(texts[i:i+16], return_tensors="pt", padding=True)
            h = model(**batch).hidden_states[layer]          # [B, T, 768]
            mask = batch["attention_mask"].unsqueeze(-1)      # [B, T, 1]
            if pool == "mean":
                v = (h * mask).sum(1) / mask.sum(1)
            else:                                             # last real token
                idx = batch["attention_mask"].sum(1) - 1
                v = h[torch.arange(h.size(0)), idx]
            out.append(v)
    return torch.cat(out).numpy()

def load_split(path):
    rows = json.load(open(path))
    return [r["text"] for r in rows], np.array([r["label"] for r in rows])
