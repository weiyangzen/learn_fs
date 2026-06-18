# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdps1.c

This file implements Display PostScript graphics additions.

Main functions:
- `gs_setbbox` sets or expands the current path bounding box after transforming user-space bounds to device fixed coordinates.
- `gs_rectappend` appends one or more rectangles to the current path in counter-clockwise order.
- `gs_rectclip` clips to a list of rectangles while preserving/restoring the previous path during construction.
- `gs_rectfill` efficiently fills rectangle lists, using direct device rectangle fills when possible.
- `gs_rectstroke` strokes rectangle lists, optionally concatenating a matrix.

`gs_rectfill` contains the most complex logic:
- It fast-paths orthogonal CTMs, rectangular clip paths, simple device colors, loaded colors, low alpha bits, and no effective overprint.
- It supports high-level device color fill through `fill_rectangle_hl_color` when available.
- It falls back to path construction plus `gs_fill` for complex cases or transform failures.

The file is performance-sensitive for common rectangle painting operations while preserving general path fallback semantics.
