# Builds data/parlasent.csv from the ParlaSent 1.0 files in data/raw/.
# Source: Mochtak, M., Rupnik, P. & Ljubesic, N. (2023) The multilingual sentiment dataset of
# parliamentary debates ParlaSent 1.0. CLARIN.SI, http://hdl.handle.net/11356/1868. CC BY-SA 4.0.
library(jsonlite)

scale6 <- c(Negative = 0, M_Negative = 1, N_Neutral = 2, P_Neutral = 3, M_Positive = 4, Positive = 5)
files  <- c(EN = "ParlaSent_EN.jsonl", CZ = "ParlaSent_CZ.jsonl",
            EN_test = "ParlaSent_EN_test.jsonl", BCS_test = "ParlaSent_BCS_test.jsonl")

read_one <- function(tag) {
  d <- stream_in(file(file.path("data", "raw", files[[tag]])), verbose = FALSE)
  test <- grepl("_test", tag)
  data.frame(file     = tag,
             country  = d$country,
             sentence = d$sentence,
             y        = unname(scale6[if (test) d$annotator1 else d$reconciliation]),  # final code, 0-5
             y_a1     = unname(scale6[d$annotator1]),                                   # first coder
             y_a2     = if (test) NA_real_ else unname(scale6[d$annotator2]),            # second coder
             label3   = d$label,
             party    = d$party,
             ruling   = d$ruling,
             date     = d$date,
             gender   = d$gender,
             stringsAsFactors = FALSE)
}

ps <- do.call(rbind, lapply(names(files), read_one))
stopifnot(!anyNA(ps$y))
write.csv(ps, file.path("data", "parlasent.csv"), row.names = FALSE)
table(ps$file, ps$country)
