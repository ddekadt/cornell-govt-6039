# Section 9: Forests, Boosting, Splines and GAMs on Survey Data

GOVT 6039, Fall 2026. Discussion section on Lectures 16 (trees, random forests and boosting) and 17 (splines and GAMs), applied to the 2016 CCES.

## Files

| File | What it is |
|---|---|
| `section09.qmd`, `.html`, `.pdf` | Student version |
| `section09_instructor.qmd`, `.html`, `.pdf` | Instructor version with worked answers (toggles in the HTML, red in the PDF) |
| `section09.lua` | Quarto filter that draws the algorithm boxes and formats the answers (both versions use it) |
| `data/cces16_vote.csv` | Analysis file: 38,615 respondents of the 2016 CCES who reported a presidential vote and answered every item used |
| `data/cache/` | Saved results of the slow steps (forests, boosting, bootstrap, CatBoost), loaded by default |
| `data/learning_curve.rds` | Results for the learning-curve figure (question 6.2) |
| `learning_curve.R` | Recomputes `data/learning_curve.rds` (about 3 to 4 minutes) |
| `prep_data.R` | Rebuilds `data/cces16_vote.csv` from the `TV16` data in the `stevedata` package |

## Rendering

```bash
quarto render section09.qmd                 # student version
quarto render section09_instructor.qmd      # instructor version (both need section09.lua in the same folder)
```

**Run time.** With the saved results in `data/cache/` (the default, `refit <- FALSE` near the top of each `.qmd`) the computations take well under a minute. Set `refit <- TRUE` to refit every model: about 2 to 3 minutes on a laptop. Each slow chunk is labelled with its approximate time.

R packages: `ggplot2`, `patchwork`, `ranger`, `gbm`, `splines`, `mgcv`, `knitr`, `rmarkdown`. The CatBoost appendix also needs `catboost`, which is not on CRAN: download the build for your system from <https://github.com/catboost/catboost/releases> (for 1.2.10: `catboost-R-darwin-universal2-1.2.10.tgz`, `catboost-R-linux-x86_64-1.2.10.tgz` or `catboost-R-windows-x86_64-1.2.10.tgz`) and run `R CMD INSTALL <file>`. Without it the appendix still renders from the saved results in `data/cache/`; only refitting needs the package.

Rendered with R 4.3.3, Quarto 1.6.42, ranger 0.16.0, gbm 2.1.8.1, mgcv 1.9.1, catboost 1.2.10. All random steps are seeded (6039).

## Data

Ansolabehere, S. & Schaffner, B. F. (2017) *Cooperative Congressional Election Study, 2016: Common Content*. Harvard Dataverse. Extract via Miller, S. V. `stevedata` (github.com/svmiller/stevedata). The analysis is unweighted.
