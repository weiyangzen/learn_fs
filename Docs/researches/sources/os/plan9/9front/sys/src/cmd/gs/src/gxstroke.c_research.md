# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxstroke.c

Implements Ghostscript path stroking: line-width expansion, cap/join construction, dash expansion, clipping, direct device fills, and strokepath outline generation.

Key behavior:
- `gx_stroke_path_expansion` computes conservative or exact bbox expansion for stroked paths, accounting for CTM, line width, caps, joins, miter limit, triangular joins, and curve joins.
- `gx_default_stroke_path` delegates to `gx_stroke_path_only`.
- `gx_stroke_path_only_aux` is the main engine. It computes orientation/reflection, expands and clips the path bbox, flattens curves, expands dashes, handles degenerate subpaths, computes segment widths, and emits either fills or path outlines.
- Optimized cases draw thin lines with `draw_thin_line` or fill bevel/miter bodies directly using `fill_triangle` and `fill_parallelogram`.
- General cases construct stroke outline paths through `stroke_add`, then fill them.
- Handles round, butt, square, and triangular caps, plus bevel, round, miter, triangle, and no-join behavior.
- `line_join_points` computes bevel/miter/triangle join points with miter-limit checks and optional inverse distance transforms for non-uniform CTMs.
- `add_round_cap` builds a full circular cap with four partial arcs.

Dependencies:
- Uses imager and line state from `gxistate.h` / `gzline.h`.
- Uses path internals from `gzpath.h`, clipping from `gzcpath.h`, and painting from `gxpaint.h`.
- Uses device procedures such as `draw_thin_line`, `fill_triangle`, `fill_parallelogram`, and clipping-device wrappers.
- Uses visual debug tracing through `vdtrace.h`.

Research notes:
- Degenerate subpaths are treated carefully: round caps can paint dots, while other caps generally do not, matching PostScript stroke behavior.
- The code has several performance-specialized branches for portrait/landscape/uniform transforms and idempotent raster operations.
- Comments acknowledge historical uncertainty around fill adjustment for strokes and orientation optimizations.
