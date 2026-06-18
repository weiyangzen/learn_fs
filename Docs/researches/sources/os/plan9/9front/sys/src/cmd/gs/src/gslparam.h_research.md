# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gslparam.h

Defines line cap and line join enum values.

Key definitions:
- `gs_line_cap`: butt, round, square, triangle, unknown.
- `gs_line_cap_max` is `3`, so `gs_cap_unknown` is not settable.
- `gs_line_join`: miter, round, bevel, none, triangle, unknown.
- `gs_line_join_max` is `4`, so `gs_join_unknown` is not settable.

Research notes:
- Some enum values are explicitly marked as not supported by PostScript but still available to Ghostscript extensions.
