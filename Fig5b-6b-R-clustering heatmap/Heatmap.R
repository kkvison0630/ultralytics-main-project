# Run from this directory: Rscript --vanilla "clustering heatmap-R-Fig5b-Fig6b.R"
if (!requireNamespace("pheatmap", quietly = TRUE)) {
  stop("Install pheatmap as described in README.md.")
}

inputs <- c(Fig5b = "Fig5b-body-z.csv", Fig6b = "Fig6b-heart-z.csv")
expected_rows <- list(
  Fig5b = c("HA", "EA", "PA", "YA", "BL"),
  Fig6b = c("SV-BA", "CO", "QTcF", "QTcB", "HR", "QT", "RR", "ESA", "EDA",
            "FS", "EF", "FAC", "SV", "ESV", "EDV")
)
palette <- grDevices::colorRampPalette(c(
  "#E6F3FF", "#A8D8EA", "#8DCCE3", "#7ACCCE", "#78D6B9",
  "#8AE0B9", "#FFFAE6", "#FFD6B8", "#FF9A76"
))(100)
dir.create("outputs", showWarnings = FALSE)

for (fig in names(inputs)) {
  input <- inputs[[fig]]
  if (!file.exists(input)) stop("Missing ", input, ". Run from the heatmap folder.")
  tab <- utils::read.csv(input, row.names = 1, check.names = FALSE)
  if (!identical(rownames(tab), expected_rows[[fig]]) ||
      ncol(tab) != 13L || anyDuplicated(colnames(tab)) ||
      any(!nzchar(colnames(tab))) || !all(vapply(tab, is.numeric, logical(1)))) {
    stop("Unexpected endpoint labels, chemical labels, or values in ", input)
  }
  mat <- as.matrix(tab)
  if (any(!is.finite(mat))) stop("Non-finite values in ", input)
  chemical_distances <- stats::dist(t(mat), method = "euclidean")
  chemical_tree <- stats::hclust(chemical_distances, method = "complete")
  output <- file.path("outputs", paste0(fig, "_heatmap.pdf"))
  pheatmap::pheatmap(
    mat, scale = "none", cluster_rows = FALSE, cluster_cols = chemical_tree,
    breaks = seq(-3.5, 3.5, length.out = 101), color = palette,
    legend_breaks = c(-3.5, -1.7, 0, 1.7, 3.5), display_numbers = FALSE,
    fontfamily = "serif", treeheight_col = 40,
    filename = output, width = 10, height = 7, silent = TRUE
  )
  writeLines(colnames(mat)[chemical_tree$order],
             file.path("outputs", paste0(fig, "_column_order.txt")))
  message("Saved ", output)
}

writeLines(
  c(capture.output(utils::sessionInfo()),
    paste("pheatmap:", as.character(utils::packageVersion("pheatmap"))),
    paste("RColorBrewer:", as.character(utils::packageVersion("RColorBrewer")))),
  file.path("outputs", "sessionInfo.txt")
)
