# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/rectclip.c

Provides in-place rectangle intersection.

Key function:
- `rectclip`: checks overlap, then clamps the first rectangle to the bounds of the second.

Important behavior:
- Expands the overlap test inline rather than calling `rectXrect`, explicitly for speed.
- Returns `0` when the rectangles do not overlap and `1` after successful clipping.
