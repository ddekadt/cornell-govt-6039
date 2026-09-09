## GOVT 6039 - Discussion Section 2, 9 September 2026
## Choosing the knobs: tuning, folds, and what cross-validation is for.
## Only lecture 1-4 machinery: squared loss / MSE, OLS, k-NN, K-fold CV.
set.seed(6039)

## =====================================================================
## PART 1.  The linear interaction model is an untuned flexibility choice.
##          Hainmueller, Mummolo & Xu (2019, Political Analysis)
## =====================================================================
u <- "https://raw.githubusercontent.com/xuyiqing/interflex/master/data/interflex.RData"
if (!file.exists("interflex.RData")) download.file(u, "interflex.RData", mode = "wb")
load("interflex.RData")          # -> app_vernby2013, app_hma2015, ...

## --- Vernby (2013, AJPS): noncitizen suffrage and school spending -----
v <- app_vernby2013              # 183 Swedish municipalities
m <- lm(school_diff ~ noncitvotsh * Taxbase2, data = v)
summary(m)$coefficients          # interaction t = -3.16

b  <- coef(m)
qs <- quantile(v$Taxbase2, c(.05, .25, .5, .75, .95))
b["noncitvotsh"] + b["noncitvotsh:Taxbase2"] * qs    # 11.7 ... -2.7

## The published story: the effect REVERSES in rich municipalities.
## Now relax the knob. HMX binning estimator: thirds of the moderator,
## estimated separately, no functional form imposed across them.
v$bin <- cut(v$Taxbase2, quantile(v$Taxbase2, c(0, 1/3, 2/3, 1)),
             labels = c("low", "mid", "high"), include.lowest = TRUE)
do.call(rbind, lapply(levels(v$bin), function(L) {
  z <- v[v$bin == L, ]; f <- lm(school_diff ~ noncitvotsh, data = z)
  data.frame(bin = L, n = nrow(z), me = coef(f)[2],
             se = summary(f)$coefficients[2, 2])
}))
## 14.10 (2.96) | 7.07 (2.66) | 2.77 (2.96)
## The decline is in the data. The sign flip is in the straight line.

## --- Huddy, Mason & Aaroe (2015, APSR): the honest counterpart --------
h <- app_hma2015                 # n = 1482; threat (randomised) x partisan identity
summary(lm(totangry ~ threat * pidentity, data = h))$coefficients

## k-NN inside each arm; k by 10-fold CV. Marginal effect = gap between
## the two local averages. (Lecture 3's estimator, lecture 4's selection.)
knn1 <- function(xtr, ytr, xte, ks) {
  M <- outer(xte, xtr, function(a, b) (a - b)^2)
  out <- matrix(NA_real_, length(xte), length(ks))
  for (i in seq_along(xte)) {
    o <- order(M[i, ]); out[i, ] <- (cumsum(ytr[o]) / seq_along(o))[ks]
  }
  out
}
cvk1 <- function(x, y, ks, K = 10) {
  set.seed(6039); f <- sample(rep(1:K, length.out = length(y)))
  M <- matrix(NA_real_, K, length(ks))
  for (j in 1:K) M[j, ] <- colMeans((y[f == j] - knn1(x[f != j], y[f != j], x[f == j], ks))^2)
  colMeans(M)
}
ks <- c(5, 10, 25, 50, 100, 200, 400)
for (d in 0:1) {
  z <- h[h$threat == d, ]
  cat("arm", d, "picks k =", ks[which.min(cvk1(z$pidentity, z$totangry, ks))], "\n")
}                                 # 400 and 200: the data want heavy smoothing

g <- seq(quantile(h$pidentity, .05), quantile(h$pidentity, .95), length.out = 9)
me <- function(k) knn1(h$pidentity[h$threat == 1], h$totangry[h$threat == 1], g, k)[, 1] -
                  knn1(h$pidentity[h$threat == 0], h$totangry[h$threat == 0], g, k)[, 1]
round(me(5),   2)   # untuned, too flexible: wanders, even goes negative
round(me(400), 2)   # CV's choice:           0.25 ... 0.37
round(coef(lm(totangry ~ threat * pidentity, data = h))["threat"] +
      coef(lm(totangry ~ threat * pidentity, data = h))["threat:pidentity"] * g, 2)
                    # linear:                0.16 ... 0.44  (steeper than the data)

## =====================================================================
## PART 2.  The folds are a knob too.  V-Dem v15 country-year panel.
## =====================================================================
uv <- "https://raw.githubusercontent.com/vdeminstitute/vdemdata/master/data/vdem.RData"
if (!file.exists("vdem_slim.rds")) {
  if (!file.exists("vdem.RData")) download.file(uv, "vdem.RData", mode = "wb")  # 34 MB
  load("vdem.RData")
  saveRDS(vdem[, c("country_name","year","v2x_polyarchy","e_gdppc","e_pop",
                   "e_total_resources_income_pc","e_regionpol_6C")], "vdem_slim.rds")
  rm(vdem); gc()
}
vd <- readRDS("vdem_slim.rds")
vd <- vd[vd$year >= 1960 & vd$year <= 2023, ]; vd <- vd[complete.cases(vd), ]
vd$lgdp <- log(pmax(vd$e_gdppc, .01)); vd$lpop <- log(pmax(vd$e_pop, .01))
vd$lres <- log1p(pmax(vd$e_total_resources_income_pc, 0))
reg <- model.matrix(~ factor(e_regionpol_6C) - 1, data = vd)[, -1, drop = FALSE]
X <- cbind(as.matrix(vd[, c("lgdp","lpop","lres","year")]), reg)
y <- vd$v2x_polyarchy; ctry <- vd$country_name
c(n = nrow(vd), countries = length(unique(ctry)), var_y = var(y))   # 6697, 163, 0.081

## k-NN over all k at once. Standardise INSIDE the fold.
knn_all <- function(Xtr, ytr, Xte, ks) {
  mu <- colMeans(Xtr); sdv <- apply(Xtr, 2, sd); sdv[sdv == 0] <- 1
  A <- scale(Xtr, mu, sdv); B <- scale(Xte, mu, sdv)
  Dm <- outer(rowSums(B^2), rowSums(A^2), "+") - 2 * B %*% t(A)
  out <- matrix(NA_real_, nrow(B), length(ks))
  for (i in seq_len(nrow(B))) {
    o <- order(Dm[i, ]); out[i, ] <- (cumsum(ytr[o]) / seq_along(o))[ks]
  }
  out
}
cv <- function(fold, ks) {
  M <- matrix(NA_real_, max(fold), length(ks))
  for (j in 1:max(fold)) {
    tr <- fold != j; te <- fold == j
    M[j, ] <- colMeans((y[te] - knn_all(X[tr, ], y[tr], X[te, ], ks))^2)
  }
  colMeans(M)
}
ks2 <- c(1, 2, 3, 5, 10, 25, 50, 100, 250, 500)

## (A) folds drawn at random, exactly as on Tuesday
set.seed(6039); fr <- sample(rep(1:10, length.out = nrow(vd)))
A <- cv(fr, ks2)
data.frame(k = ks2, mse = round(A, 4), R2 = round(1 - A / var(y), 3))
## k = 2 wins at MSE 0.0016 -- an R2 of 0.98. Do we believe it?

## (B) hold out whole COUNTRIES
set.seed(6039); uc <- unique(ctry)
fb <- sample(rep(1:10, length.out = length(uc)))[match(ctry, uc)]
B <- cv(fb, ks2)
data.frame(k = ks2, random = round(A, 4), blocked = round(B, 4))
c(k_random = ks2[which.min(A)], k_blocked = ks2[which.min(B)])       # 2 vs 100
c(reported = min(A), honest_at_that_k = B[which.min(A)])             # 0.0016 vs 0.0496

## OLS, both ways, for scale
cvo <- function(fold) {
  df <- as.data.frame(X)
  mean(sapply(1:max(fold), function(j) {
    tr <- fold != j; te <- fold == j
    mean((y[te] - predict(lm(y[tr] ~ ., data = df[tr, ]), df[te, ]))^2)
  }))
}
c(ols_random = cvo(fr), ols_blocked = cvo(fb))                       # 0.0327, 0.0345

## Denmark 1994 and Denmark 1995 are nearly the same row. Random folds put
## one in training and the other in test, so k = 2 is a lookup table keyed
## on country. Block by country and the key is gone.
