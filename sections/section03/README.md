# Discussion Section 3 — 16 September 2026

## Penalized regression and covariate selection for causal estimates

Follows Lecture 5 (*Penalization*, ISL 6.1–6.2). Everything here uses only material from
Lectures 1–5: squared-error loss, OLS, cross-validation, ridge, lasso and the elastic net.

### Start here

Open **`section03.html`** in a browser. It is self-contained and needs no other file in this
folder.

To run the code yourself, the document carries its own instructions under "Getting this running":
clone the repo (or sparse-checkout this one folder), or `curl` the `.qmd` on its own. It downloads
its own data on first render, so no data files are needed to start.

### What the section covers

Lecture 5 slide 3 lists two causal motivations for penalization that the lecture does not return
to. Slide 27 shows what happens when the penalty is pointed at a coefficient you wanted to
interpret. Both are picked up here.

- **Part 1** rebuilds slide 27. The same ridge fit, run twice, differing only in whether the age
  terms sit inside the penalty. Penalized, the linear age coefficient collapses from 3.8 to 0.35
  and the fitted curve takes the wrong shape.
- **Part 2** is the causal case, on simulated data where the truth is known. Selecting controls
  with a single lasso of the outcome on treatment and covariates is biased: it recovers a
  treatment effect of 1.40 against a truth of 1.00, barely better than using no controls at all.
  Post-double-selection (Belloni, Chernozhukov & Hansen 2014) returns 0.98. The diagnostic table
  explains why. A lasso of Y on X alone finds all 20 confounders, but once D is in the regression
  it absorbs their signal and the penalty drops them.
- **Part 3** applies the same three estimators to Gerber, Green & Larimer (2008), including the
  four treatment mailings from the paper's Appendix A. At the full 229,444 observations you do not
  need penalization at all. At a realistic survey-experiment size of 1,000, four raw covariates
  expand to a 134-column dictionary, OLS on all of it is *less* precise than a raw difference in
  means, and post-double-selection is the most precise of the three.
- **Part 4** covers when not to use this, plus post-selection inference and correlated columns. It
  also treats the case where $p$ is *too* large: the lasso's guarantees need $s \log p / n \to 0$,
  so sparsity rather than $p$ is the binding constraint. A collapsed optional section explains
  square-root lasso, whose theoretical penalty does not depend on the unknown noise scale
  (Belloni, Chernozhukov & Wang 2011; Sun & Zhang 2012), and sets a starred exercise in which
  students show that the ordinary lasso's cross-validated penalty tracks $\sigma$ while
  $\lambda/\sigma$ sits near $\sqrt{\log p / n}$.

Part 3 opens by setting out what the GGL study is aiming at, using the Slough and Tyson (2023)
decomposition that section 2 introduced: setting, contrast, measurement strategy, mechanism and
empirical target. Two causal diagrams carry the contrast between Parts 2 and 3. In the
observational case both arrows out of X are live and control choice determines whether the
estimate is right. Under randomisation there is no arrow into D, no covariate can confound, and
covariates are there only to reduce variance.

One caveat is flagged in the document. GGL randomised households, our extract has no household
identifier, so nothing here is clustered and the absolute standard errors are too small. The
comparison between estimators is unaffected.

### Rebuilding

```bash
quarto render section03.qmd            # both formats
quarto render section03.qmd --to html  # or one at a time
quarto render section03.qmd --to pdf
```

Needs `glmnet`, `ggplot2`, `ggrepel` and `DT`, and a LaTeX installation for the PDF. Both
diagrams are drawn in R rather than Mermaid, so neither format needs a headless browser.

The two simulations are about 260 cross-validated lasso fits and take roughly four minutes. Their
results are stored in `data/sim_results.rds`, which ships with this folder, so a normal render
takes well under a minute and gives identical numbers on any machine. The document remains the
only source of truth: the chunks recompute and re-save if that file is missing, so **delete
`data/sim_results.rds` to rebuild the simulations from scratch**. Seeds are fixed, so a rebuild
reproduces the same values.

### Files

| file | what it is |
|:--|:--|
| `section03.qmd` / `.html` / `.pdf` | the walkthrough, source and rendered |
| `data/social_slim.rds` | Control and Neighbors arms of Gerber, Green & Larimer (2008), six columns |
| `data/sim_results.rds` | precomputed output of the two simulations, so renders are fast |
| `images/*.png` | the four treatment mailings, from Appendix A of the published paper |

`social_slim.rds` is 229,444 rows extracted from the copy distributed with Imai's *Quantitative
Social Science* (<https://github.com/kosukeimai/qss>), restricted to two treatment arms and the
four pre-treatment covariates the section uses.
