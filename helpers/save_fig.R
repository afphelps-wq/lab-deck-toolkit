# save_fig(): save a figure plus a caption sidecar so the weekly deck can use it.
# source("~/lab-deck-toolkit/helpers/save_fig.R")
# save_fig(p, "tnk_umap_res0.8",
#          caption = "TNK subclusters at res 0.8; 18 clusters, TNK 17 = CXCL13+ Tph",
#          params = list(resolution = 0.8, n_pcs = 30))
# Then commit both files: figures/tnk_umap_res0.8.png and .json

save_fig <- function(p, name, caption, params = list(), dir = "figures",
                     width = 7, height = 5, dpi = 200) {
  stopifnot(nzchar(caption))
  dir.create(dir, showWarnings = FALSE, recursive = TRUE)
  png_path <- file.path(dir, paste0(name, ".png"))
  if (inherits(p, "ggplot") || inherits(p, "patchwork")) {
    ggplot2::ggsave(png_path, p, width = width, height = height, dpi = dpi)
  } else {
    grDevices::png(png_path, width = width, height = height, units = "in", res = dpi)
    print(p)
    grDevices::dev.off()
  }
  script <- tryCatch(rstudioapi::getSourceEditorContext()$path, error = function(e) NA)
  if (is.na(script) || !nzchar(script)) {
    a <- grep("^--file=", commandArgs(FALSE), value = TRUE)
    script <- if (length(a)) sub("^--file=", "", a[1]) else NA
  }
  meta <- list(
    caption = caption,
    created = format(Sys.time(), "%Y-%m-%dT%H:%M:%S"),
    script = script,
    params = params,
    code_commit = tryCatch(system("git rev-parse --short HEAD", intern = TRUE),
                           error = function(e) NA)
  )
  jsonlite::write_json(meta, file.path(dir, paste0(name, ".json")),
                       auto_unbox = TRUE, pretty = TRUE)
  kb <- file.info(png_path)$size / 1024
  if (kb > 1024) warning(sprintf("%s is %.0f KB; keep figures under 1 MB for git", png_path, kb))
  invisible(png_path)
}
