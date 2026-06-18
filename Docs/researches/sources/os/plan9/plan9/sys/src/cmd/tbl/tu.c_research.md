# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tu.c

Draws horizontal rules and identifies vertical rule extents.

Key functions:
- `makeline` draws a horizontal rule segment for one cell or span.
- `fullwide` draws table-wide horizontal rules while skipping vertical spans.
- `drawline` emits troff line drawing escapes, with endpoint adjustments based on `interv`.
- `getstop` assigns line-stop registers for vertical line starts.
- `left` finds the starting row and width of a vertical line ending at a position.
- `lefdata` returns vertical line kind from format state and box/allbox flags.
- `next` and `prev` skip non-data rows.

Notable behavior:
- Double rules draw two offset lines unless `pr1403` mode collapses them.
- Short line entries are detected by leading backslash.
