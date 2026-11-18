"""Convert prep_embeddings.py's .npz outputs into the .rds files the .qmd reads.
Run after prep_embeddings.py: python3 convert_cache.py && Rscript convert_cache.R"""
import os, numpy as np
C = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cache")
A = np.load(os.path.join(C, "A_test.npz")); H = np.load(os.path.join(C, "A_head.npz"))
out = {"A_row": A["row"] + 1, "A_u20": A["u"][:20], "A_yhat": A["yhat"],
       "H_W": H["W"], "H_w0": H["w0"], "H_beta": H["beta"], "H_beta0": H["beta0"]}
if os.path.exists(os.path.join(C, "B_cz.npz")):
    B = np.load(os.path.join(C, "B_cz.npz"))
    out.update({"B_row": B["row"] + 1, "B_u": B["u"]})
for k, v in out.items():
    v = np.asarray(v, dtype=np.float64)
    v.ravel(order="F").tofile(os.path.join(C, k + ".bin"))   # R matrices are column-major
    with open(os.path.join(C, k + ".dim"), "w") as f:
        f.write(" ".join(map(str, v.shape)))
