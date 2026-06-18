# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdps1.c

## Role

`gsdps1.c` implements Display PostScript graphics additions: explicit path bbox setting and rectangle append/clip/fill/stroke operations.

## Main Functions

- `gs_setbbox` transforms a user-space bbox to device fixed coordinates, applies rounding slack, unions it with any existing path bbox, and marks the path bbox as set.
- `gs_rectappend` appends one or more rectangles to the current path with counter-clockwise orientation.
- `gs_rectclip` temporarily replaces the current path with rectangles, clips, restores/free path state, and clears the path.
- `gs_rectfill` fills rectangles, with a fast path for orthogonal CTMs, rectangular clips, supported color types, loaded device color, no graphics antialiasing, and no effective overprint mode.
- `gs_rectstroke` appends rectangles, optionally concatenates a matrix, and strokes.

## Fast Path

`gs_rectfill` transforms rectangle corners to fixed coordinates and directly invokes high-level color rectangle fill or `gx_fill_rectangle` after clipping/intersection. It falls back to path construction plus `gs_fill` on transform/conversion/color failures.

## Dependencies

Uses matrix, path, clip path, fixed arithmetic, high-level device color, painting, and graphics-state APIs.

## Risks

The fast path has many preconditions; fallback preserves correctness but can be slower. `gs_setbbox` depends on fixed-coordinate limits and adds fixed epsilon slack to avoid rounding underestimation.
