"""Precompute the network outputs used in Section 10 (run once; not needed to render).

Two pretrained networks from the ParlaMint project, both XLM-R-large (24 layers):
  A. classla/xlm-r-parlasent : fine-tuned to score sentiment on 0-5 (the head is used as is)
  B. classla/xlm-r-parla     : pretrained on parliamentary text only, never shown a sentiment label

For each sentence x the 24 layers return 1,024 numbers per word piece. For network A, u(x) is the vector
at the <s> token, which its sentiment head reads. Network B was never trained to summarise a sentence at
<s>, so its u(x) is the average over the sentence's word pieces. Network A then applies its head: b = tanh(w0 + W u), yhat = beta0 + beta' b.

Writes to data/cache/:
  A_test.npz   row (0-based, in the two test files stacked), u, b and yhat: 1,500 sentences from each test file
  A_head.npz   the head's weights W (1024 x 1024), w0 (1024), beta (1024), beta0 (1)
  B_cz.npz     row and u (mean over word pieces) from network B for 2,000 sentences of the Czech file
Takes about 20 to 50 minutes on a 4-core laptop CPU, plus a 4.5 GB download. Needs torch, transformers, pandas, numpy.
"""
import os, sys, time, numpy as np, pandas as pd, torch
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "cache")
os.makedirs(OUT, exist_ok=True)
torch.set_num_threads(os.cpu_count())
REV_A = "d2b85face108b9a2ad36aa793115810f5efd783b"   # classla/xlm-r-parlasent, the version used here
REV_B = "61eb1e2da799aad1d2aecbe0e7191ff2aa21b109"   # classla/xlm-r-parla
tok = AutoTokenizer.from_pretrained("classla/xlm-r-parlasent", revision=REV_A)
N_TEST, N_CZ = 1500, 2000          # sentences drawn from each test file, and from the Czech file


def run(encoder, texts, head=None, bs=32, label="", pool="cls"):
    """Return u (n x 1024), and b, yhat if a head is given. Batches by length to save padding."""
    n = len(texts)
    order = sorted(range(n), key=lambda i: len(texts[i]))
    U = np.zeros((n, 1024), np.float32)
    Bm = np.zeros((n, 1024), np.float32) if head is not None else None
    Y = np.zeros(n, np.float32) if head is not None else None
    t0 = time.time()
    with torch.no_grad():
        for s in range(0, n, bs):
            ii = order[s:s + bs]
            enc = tok([texts[i] for i in ii], padding=True, truncation=True,
                      max_length=256, return_tensors="pt")
            h = encoder(**enc).last_hidden_state
            if pool == "mean":           # average over the sentence's word pieces, padding excluded
                m = enc["attention_mask"].unsqueeze(-1).float()
                u = (h * m).sum(1) / m.sum(1)
            else:                        # the vector at the <s> token, which the sentiment head reads
                u = h[:, 0, :]
            U[ii] = u.numpy()
            if head is not None:
                b = torch.tanh(head.dense(u))
                Bm[ii] = b.numpy()
                Y[ii] = head.out_proj(b).squeeze(-1).numpy()
            if (s // bs) % 10 == 0:
                print(f"{label} {s + len(ii)}/{n} {time.time() - t0:.0f}s", flush=True)
    return U, Bm, Y


def read(name):
    return pd.read_json(os.path.join(HERE, "data", "raw", name), lines=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("A", "all"):
        mA = AutoModelForSequenceClassification.from_pretrained("classla/xlm-r-parlasent", revision=REV_A).eval()
        h = mA.classifier
        np.savez(os.path.join(OUT, "A_head.npz"), W=h.dense.weight.detach().numpy(),
                 w0=h.dense.bias.detach().numpy(), beta=h.out_proj.weight.detach().numpy().ravel(),
                 beta0=h.out_proj.bias.detach().numpy())
        test = pd.concat([read("ParlaSent_EN_test.jsonl"), read("ParlaSent_BCS_test.jsonl")], ignore_index=True)
        # a random 1,500 sentences from each test file keeps the run under an hour on a laptop CPU
        rng = np.random.default_rng(6039)
        rows = np.sort(np.concatenate([rng.choice(2600, N_TEST, replace=False),
                                       2600 + rng.choice(2600, N_TEST, replace=False)]))
        test = test.iloc[rows]
        U, Bm, Y = run(mA.roberta, test["sentence"].astype(str).tolist(), head=h, label="A")
        # check: our forward pass through the head equals the model's own output
        with torch.no_grad():
            enc = tok(test["sentence"].astype(str).tolist()[:4], padding=True, return_tensors="pt")
            own = mA(**enc).logits.squeeze(-1).numpy()
        print("head check (max abs diff):", float(np.abs(own - Y[:4]).max()), flush=True)
        np.savez(os.path.join(OUT, "A_test.npz"), row=rows, u=U, b=Bm, yhat=Y)
    if which in ("B", "all"):
        # xlm-r-parla ships only a pickled pytorch_model.bin, which recent transformers refuse to read
        # with torch < 2.6; build the masked-language model from its config and load the weights directly
        from huggingface_hub import hf_hub_download
        from transformers import AutoConfig, AutoModelForMaskedLM
        cfg = AutoConfig.from_pretrained("classla/xlm-r-parla", revision=REV_B)
        mlm = AutoModelForMaskedLM.from_config(cfg)
        sd = torch.load(hf_hub_download("classla/xlm-r-parla", "pytorch_model.bin", revision=REV_B),
                        map_location="cpu")
        missing, unexpected = mlm.load_state_dict(sd, strict=False)
        print("missing:", missing, "unexpected:", unexpected, flush=True)
        mB = mlm.roberta.eval()
        cz = read("ParlaSent_CZ.jsonl")
        rows = np.sort(np.random.default_rng(6039).choice(2600, N_CZ, replace=False))
        U, _, _ = run(mB, cz["sentence"].iloc[rows].astype(str).tolist(), label="B", pool="mean")
        np.savez(os.path.join(OUT, "B_cz.npz"), row=rows, u=U)
    print("DONE", flush=True)
