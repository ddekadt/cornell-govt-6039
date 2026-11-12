## Rebuilds data/cces16_vote.csv, the analysis file for Section 9.
##
## Source: the TV16 data in Steven Miller's {stevedata} package (github.com/svmiller/stevedata),
## an extract of the 2016 Cooperative Congressional Election Study (Ansolabehere & Schaffner 2017).
## Not needed to render the section: the output file is already in data/.
##
## usage: Rscript prep_data.R                 (downloads TV16.rda from GitHub)
##        Rscript prep_data.R path/to/TV16.rda
args <- commandArgs(trailingOnly = TRUE)
src  <- if (length(args) >= 1) args[1] else {
  tmp <- tempfile(fileext = ".rda")
  download.file("https://github.com/svmiller/stevedata/raw/master/data/TV16.rda", tmp, mode = "wb")
  tmp
}
load(src); d <- as.data.frame(TV16)

d$race <- ifelse(d$racef %in% c("White", "Black", "Hispanic", "Asian"), d$racef, "Other")
keep <- c("votetrump", "state", "age", "female", "collegeed", "race", "famincr", "lrelig",
          "pid7na", "ideo", "lcograc", "lemprac")
d <- d[complete.cases(d[, keep]), keep]                 # voters with every item answered
names(d)[names(d) == "votetrump"] <- "trump"
names(d)[names(d) == "pid7na"]    <- "pid7"
num <- sapply(d, is.double); d[num] <- lapply(d[num], round, 4)
dir.create("data", showWarnings = FALSE)
write.csv(d, "data/cces16_vote.csv", row.names = FALSE)
cat(nrow(d), "respondents;", round(mean(d$trump), 3), "voted Trump\n")
