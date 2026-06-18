# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsimpath.c

## Role

`gsimpath.c` converts a 1-bit image mask into vector outlines appended to the current path.

This is image/path rendering infrastructure, not filesystem code.

## Main Interface

`gs_imagepath(gs_state *pgs, int width, int height, const byte *data)`.

## Core Behavior

- Scans the bitmap from bottom-right to top-left looking for outline start pixels.
- Uses `get_pixel` with out-of-bounds pixels treated as empty.
- `trace_from` walks each connected outline clockwise, optionally in detection mode to avoid duplicate tracing, using a scaled grid and short corner strokes.
- `add_dxdy` coalesces consecutive path segments in the same direction before emitting `gs_rlineto` operations.
- Completed outlines are closed with `gs_closepath`.

## Notable Risks

The algorithm assumes packed 1-bit image data with raster `(width + 7) / 8`. The infinite-looking loop in `trace_from` relies on contour topology and start-point detection to terminate; malformed dimensions or unexpected data interpretation could lead to bad path behavior.
