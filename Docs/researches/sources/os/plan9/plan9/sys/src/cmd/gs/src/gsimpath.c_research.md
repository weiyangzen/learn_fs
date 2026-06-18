# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsimpath.c

Converts a 1-bit image mask into an outline path.

Main entry:
- `gs_imagepath(gs_state *pgs, int width, int height, const byte *data)`

Algorithm:
- Scans pixels from bottom-right toward top-left.
- Detects starting boundary pixels.
- Uses `trace_from` to walk the outline clockwise.
- Emits `moveto`, `rlineto`, and `closepath` operations into the current path.
- Uses a small `outline_scale` and `step` to avoid corner backtracking and produce cleaner outlines.

Helpers:
- `get_pixel`: returns a bit from packed image data, treating out-of-bounds as empty.
- `trace_from`: follows the boundary, optionally in detect-only mode to avoid retracing.
- `add_dxdy`: coalesces repeated relative segments before appending to the path.

This is compact raster-to-vector boundary tracing for imagemask-like data.
