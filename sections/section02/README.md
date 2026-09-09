# Discussion Section 2 — 9 September 2026

## Hyperparameter tuning: an application to real political science research

Sits between Lecture 4 (*Assessing models*, ISL 5.1–5.2) and Lecture 5 (*Penalization*). Everything
here uses only material from Lectures 1–4: squared-error loss, OLS, k-NN, K-fold cross-validation
and the bias–variance trade-off. λ appears once, as a pointer to the next lecture.

### Start here

Open **`section02-replication.html`** in a browser. It is self-contained, so it needs no other file
in this folder and can be shared as a single attachment.

### What the section covers

Three published studies, each worked in the same five steps: describe the study and look at the raw
data, reproduce the published estimate, ask what that estimate assumes, relax the assumption, then
compare. Each study is introduced with its full citation, its research question, and a decomposition
into setting, contrast, measurement strategy, mechanism and empirical target, following Slough and
Tyson (2023, *AJPS* 67(2)).

- **Vernby (2013, *AJPS*)** — noncitizen suffrage and school spending in Sweden. The linear
  interaction model reports an effect that reverses sign among high-tax-base municipalities. The
  crossing point sits at the 90th percentile of the moderator, with 19 of 183 municipalities beyond
  it, and estimating within thirds of the moderator gives a positive effect there. The decline is in
  the data; the sign change is in the functional form.
- **Huddy, Mason and Aarøe (2015, *APSR*)** — threat and partisan identity. The same check, with k
  chosen by cross-validation, largely confirms the published result. Tuning is not only a way to
  overturn findings.
- **V-Dem v15** — how much of a country's level of democracy do structural conditions explain?
  Random 10-fold cross-validation selects k = 2 and reports an R² of 0.98. Drawing the folds over
  whole countries instead, the same model is 33 times worse and no better than OLS. A country-year
  correlates 0.988 with its own previous year, so random folds hand the model a near-copy of the
  answer.

### Reproducing it

R 4.1 or newer, Quarto (bundled with Positron), and two packages:

```r
install.packages(c("ggplot2", "maps"))
```

`maps` is used only for one world map, and that chunk skips itself if the package is absent.
Everything else is base R, including both estimators. Then:

```bash
quarto render section02-replication.qmd
```

Both datasets are in this folder, so the render needs no internet. A full run takes about three
minutes; chunk caching makes later renders quick. Delete `section02-replication_cache/` to force a
clean run — worth doing after any change, since stale cached output can disagree with the text
around it.

`section02_live.R` runs the same analysis as a plain script if you would rather not use Quarto.

### Files

| file | what it is |
|:--|:--|
| `section02-replication.qmd` / `.html` | the walkthrough, source and rendered |
| `section02.qmd` / `.pdf` | the section slides, source and rendered |
| `section02_live.R` | the analysis as a plain R script |
| `replication.css`, `custom.scss`, `preamble.tex`, `spans.lua` | styling for the two documents |
| `interflex.RData` | replication extracts from Vernby (2013) and Huddy, Mason & Aarøe (2015) |
| `vdem_slim.rds` | seven columns from V-Dem v15, extracted from the 34 MB original |

Data are redistributed from the `interflex` package (<https://github.com/xuyiqing/interflex>) and
V-Dem (<https://github.com/vdeminstitute/vdemdata>).
