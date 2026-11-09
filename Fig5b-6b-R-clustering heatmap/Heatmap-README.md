# Reproduce Figures 5b and 6b

This workflow regenerates the clustered heatmap panels from the standardized matrices supplied with the study. The calculation of toxicity extent scores from experimental measurements is described separately in Supporting Information Text S9.

| Input | Rows (endpoints) | Columns (LCMs) |
| --- | ---: | ---: |
| `Fig5b-body-z.csv` | 5 | 13 |
| `Fig6b-heart-z.csv` | 15 | 13 |

The first CSV column contains endpoint names. The remaining columns are chemical profiles. Row order and chemical names are preserved, including names that begin with digits. The supplied values are already standardized.

## Software

The manuscript specifies **R 4.3.3**. The recorded Windows environment uses **pheatmap 1.0.13**, with **RColorBrewer 1.1-3** as a dependency. Font registration is not required by this script; it uses a portable serif font. To install the recorded package versions in R:

```r
install.packages("remotes", repos = "https://cloud.r-project.org")
remotes::install_version("RColorBrewer", version = "1.1-3",
                         repos = "https://cloud.r-project.org", upgrade = "never")
remotes::install_version("pheatmap", version = "1.0.13",
                         repos = "https://cloud.r-project.org", upgrade = "never")
```

The commands pin these two packages; the script records the actual versions loaded at runtime.

## Run

Open a terminal in this folder, with the R script and both CSV files together:

```sh
Rscript --vanilla "clustering heatmap-R-Fig5b-Fig6b.R"
```

The script uses Euclidean distances between **chemical columns** and complete linkage, leaves the endpoint rows in their original order, and sets `scale = "none"`:

```r
chemical_distances <- stats::dist(t(mat), method = "euclidean")
chemical_tree <- stats::hclust(chemical_distances, method = "complete")
```

Both panels are saved automatically to `outputs/`:

- `Fig5b_heatmap.pdf` and `Fig6b_heatmap.pdf`
- `Fig5b_column_order.txt` and `Fig6b_column_order.txt`
- `sessionInfo.txt`

Panel typography can differ from the published layout. The input matrix, clustering rule, and color scale are specified in the script.
