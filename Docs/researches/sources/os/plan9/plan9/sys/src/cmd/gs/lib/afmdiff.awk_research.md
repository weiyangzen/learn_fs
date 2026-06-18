# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/afmdiff.awk

AWK utility for comparing two Adobe Font Metric files.

Behavior:

- Records the first two `FontName` values encountered, corresponding to the two input AFM files.
- For AFM character metric lines beginning `C `, tracks character names, declared `WX` widths, and bounding-box width/height derived from BBox fields.
- Reports character repertoire differences in both directions.
- Reports numeric differences for `WX`, bounding-box width, and bounding-box height.
- Sorts each report column through `sort -f | pr -c3 -w80 -l1 -t`.

The script is purely metrics-analysis tooling for Ghostscript font data. It has no repository-build or filesystem-layer role.
