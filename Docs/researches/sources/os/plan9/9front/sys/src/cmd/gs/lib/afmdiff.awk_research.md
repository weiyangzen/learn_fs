# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/afmdiff.awk

AWK utility by Nelson H. F. Beebe for comparing two Adobe Font Metric files.

Behavior:
- Records `FontName` values in file order.
- For each AFM character metric line beginning with `C `, records character names from the first and second files.
- Compares declared widths (`WX`) keyed by character name.
- Computes bounding-box width (`xmax - xmin`) and height (`ymax - ymin`) and records differences.
- In `END`, prints file/font names, missing character reports in both directions, and numeric difference tables.

Implementation details:
- `show_name_diffs` reports names present in one font but absent in the other.
- `show_num_diffs` prints width/height difference tables.
- Output is piped through `sort -f | pr -c3 -w80 -l1 -t` for formatted columns.

Assumptions:
- It relies on AFM character metric fields being in the conventional positions used by Ghostscript AFM files.
- It expects exactly the two input files referenced by `ARGV[1]` and `ARGV[2]`.

Filesystem relevance:
- Text-analysis utility over font metric files; no filesystem internals.
