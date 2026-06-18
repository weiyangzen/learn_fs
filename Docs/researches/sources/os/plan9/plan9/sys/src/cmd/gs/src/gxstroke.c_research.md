# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxstroke.c

Ghostscript path stroking implementation. It converts paths and line parameters into filled stroke outlines or direct device drawing operations, handling line width, dash expansion, caps, joins, clipping, thin lines, and stroke adjustment.

Key behavior:
- `gx_stroke_path_expansion` computes conservative or exact bounding-box expansion for a stroked path based on CTM, line width, caps, joins, miter limit, and path shape.
- `gx_default_stroke_path` delegates to `gx_stroke_path_only`.
- `gx_stroke_path_only_aux` is the main pipeline: computes clipping bounds, flattens curves, expands dashes, detects CTM orientation/uniform scale, computes device-space stroke widths, handles degenerate subpaths, and emits each segment.
- When drawing, `stroke_fill` uses optimized device procedures for thin lines, parallelogram bodies, and bevel triangles where possible; otherwise it falls back to constructing a stroke path.
- When building paths, `stroke_add` appends cap/join outlines to `to_path`, including round caps and round joins.
- `line_join_points` implements bevel, miter, triangle, and no-join behavior, including miter-limit checks under non-uniform transforms.
- `adjust_stroke`, `width_is_thin`, and `set_thin_widths` implement pixel-aligned stroke adjustment and minimum-width handling.
- `compute_caps`, `add_round_cap`, and `cap_points` generate butt, square, round, and triangular cap geometry.

Notable dependencies:
- Path and line internals: `gzpath.h`, `gzline.h`, `gzcpath.h`.
- Device and paint procedures: `gxdevice.h`, `gsdevice.h`, `gxpaint.h`.
- Matrix/fixed arithmetic: `gxmatrix.h`, `gxfixed.h`, `gxfarith.h`.
- Debug visualization hooks: `vdtrace.h`.

Research notes:
- The code deliberately treats zero-width and very thin lines differently from normal fills, because fill adjustment can otherwise make strokes look too heavy or disappear.
- `gx_stroke_path_only` with a non-null output path may still clip against the clipping path, which the file notes is almost never what callers of `strokepath` want.
- The implementation is optimization-heavy and geometry-sensitive; changes can affect exact scan conversion, joins at transformed angles, dash behavior, and degenerate subpaths.
