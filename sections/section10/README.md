# Section 10: Borrowing a Deep Network

GOVT 6039, Fall 2026. Discussion section on Lectures 18 (neural networks) and 19 (deep learning), applied to the sentiment of parliamentary speech in the UK, Bosnia and Herzegovina, Croatia, Serbia and Czechia.

## Files

| File | What it is |
|---|---|
| `section10.qmd`, `.html`, `.pdf` | Student version |
| `section10_instructor.qmd`, `.html`, `.pdf` | Instructor version with worked answers (toggles in the HTML, red in the PDF) |
| `section10_explainer.html` | Interactive walk-through of the section for students: animations, answers in toggles, annotated Python for each part. One self-contained file; open it in any browser. Also online at [georgytarasenko.com/teaching/govt-6039-neural-networks](https://georgytarasenko.com/teaching/govt-6039-neural-networks/) |
| `section10_home.ipynb` | The Python walk-through as a notebook, written for people new to Python. Runs in Google Colab: [open it there](https://colab.research.google.com/github/ddekadt/cornell-govt-6039/blob/main/sections/section10/section10_home.ipynb) |
| `section10_home.py` | The same walk-through as one plain script |
| `make_notebook.py`, `build_explainer.py`, `viz_template.html` | Build the notebook, the script and the explainer page |
| `section10.lua` | Quarto filter that draws the model boxes and formats the answers (same as Section 9) |
| `data/raw/` | The four ParlaSent 1.0 files used here, with the original README |
| `data/parlasent.csv` | Analysis file built from `data/raw/` by `prep_data.R` |
| `data/cache/` | Outputs of the two pretrained networks, computed once by `prep_embeddings.py` |
| `prep_data.R` | Rebuilds `data/parlasent.csv` |
| `convert_cache.py`, `convert_cache.R` | Turn the `.npz` files written by `prep_embeddings.py` into the `.rds` files in `data/cache/` |
| `prep_embeddings.py` | Recomputes `data/cache/` (Python; 20 to 50 minutes on a laptop CPU; downloads about 4.5 GB of model weights; pins the model versions used) |

New to Python? Start with [Python for R users](https://georgytarasenko.com/teaching/govt-6039-python-for-r/).

## Rendering

```bash
quarto render section10.qmd                 # student version
quarto render section10_instructor.qmd      # instructor version (both need section10.lua in the same folder)
```

R packages: `ggplot2`, `patchwork`, `Matrix`, `glmnet`, `nnet`. No Python is needed to render: the network outputs are read from `data/cache/`. The whole document renders in under a minute.

To recompute the cache: `pip install torch transformers pandas numpy`, then `python3 prep_embeddings.py && python3 convert_cache.py && Rscript convert_cache.R`. The networks are `classla/xlm-r-parlasent` and `classla/xlm-r-parla` on Hugging Face (Apache 2.0).

## Data and licence

Mochtak, M., Rupnik, P. & Ljubešić, N. (2023) *The Multilingual Sentiment Dataset of Parliamentary Debates ParlaSent 1.0*. Slovenian language resource repository CLARIN.SI, <http://hdl.handle.net/11356/1868>. Licensed CC BY-SA 4.0: the files in `data/` are shared under the same licence.
