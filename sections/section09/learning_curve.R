## Test AUC of each model as the training set grows. Takes a few minutes, so the result is cached
## in data/learning_curve.rds and section only reads it. usage: Rscript learning_curve.R
suppressMessages({library(ranger); library(gbm); library(mgcv); library(splines)})
cc <- read.csv("data/cces16_vote.csv"); cc$race <- factor(cc$race, levels = c("White", "Black", "Hispanic", "Asian", "Other"))
f  <- trump ~ age + female + collegeed + race + famincr + lrelig
auc <- function(p, y) { n1 <- sum(y == 1); n0 <- sum(y == 0); (sum(rank(p)[y == 1]) - n1 * (n1 + 1) / 2) / (n1 * n0) }

set.seed(6039)
hold <- sample(nrow(cc), 10000); te <- cc[hold, ]; pool <- cc[-hold, ]      # a fixed test set of 10,000
out <- NULL
for (n in c(250, 500, 1000, 2500, 5000, 10000, 20000)) for (r in 1:5) {
  set.seed(1000 * r + n); tr <- pool[sample(nrow(pool), n), ]
  gb  <- gbm(f, data = tr, distribution = "bernoulli", n.trees = 1200, shrinkage = 0.02, interaction.depth = 3,
             n.minobsinnode = 10, cv.folds = 3, n.cores = 1, verbose = FALSE)
  out <- rbind(out, data.frame(n = n, rep = r,
    Logit = auc(predict(glm(f, binomial, tr), te), te$trump),
    `Spline logit` = auc(predict(glm(trump ~ female + collegeed + race + ns(age, 4) + ns(famincr, 3) + ns(lrelig, 3),
                                     binomial, tr), te), te$trump),
    GAM = auc(predict(gam(trump ~ female + collegeed + race + s(age) + s(famincr, k = 8) + s(lrelig), data = tr,
                          family = binomial, method = "REML"), te), te$trump),
    `Random forest` = auc(predict(ranger(update(f, factor(trump) ~ .), tr, probability = TRUE, num.trees = 300,
                                         mtry = 2, min.node.size = 10, seed = r), te)$predictions[, 2], te$trump),
    Boosting = auc(predict(gb, te, n.trees = gbm.perf(gb, method = "cv", plot.it = FALSE)), te$trump),
    check.names = FALSE))
}
saveRDS(out, "data/learning_curve.rds")
print(round(aggregate(out[, -(1:2)], list(n = out$n), mean), 4))
