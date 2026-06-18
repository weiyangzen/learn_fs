# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrect.h

Defines rectangle utility macros and declares integer-rectangle difference.

Exports:
- `rect_within`
- `rect_intersect`
- `rect_merge`
- `int_rect_difference`
- `PARALLELOGRAM_IS_RECT`
- `INT_RECT_FROM_PARALLELOGRAM`

The macros operate on rectangle structs with `p` and `q` corners and are used by clipping/painting geometry code.
