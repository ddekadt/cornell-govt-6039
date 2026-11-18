# Second half of convert_cache.py: read the .bin files and save the .rds files used by the .qmd.
C <- file.path("data", "cache")
rd <- function(k) {
  d <- scan(file.path(C, paste0(k, ".dim")), quiet = TRUE)
  v <- readBin(file.path(C, paste0(k, ".bin")), "double", n = prod(d))
  if (length(d) == 2) matrix(v, d[1], d[2]) else v
}
saveRDS(list(row = as.integer(rd("A_row")), u = rd("A_u20"), yhat = rd("A_yhat")),
        file.path(C, "A_test.rds"), compress = "xz")
saveRDS(list(W = rd("H_W"), w0 = rd("H_w0"), beta = rd("H_beta"), beta0 = rd("H_beta0")),
        file.path(C, "A_head.rds"), compress = "xz")
if (file.exists(file.path(C, "B_row.bin")))
  saveRDS(list(row = as.integer(rd("B_row")), u = round(rd("B_u"), 4)),
          file.path(C, "B_cz.rds"), compress = "xz")
unlink(list.files(C, pattern = "\\.(bin|dim)$", full.names = TRUE))
file.size(list.files(C, pattern = "rds$", full.names = TRUE))
