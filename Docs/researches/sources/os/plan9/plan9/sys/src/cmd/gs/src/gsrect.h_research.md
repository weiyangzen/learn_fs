# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrect.h

Provides rectangle utility macros and one rectangle-difference declaration.

Key definitions:
- `rect_within`: tests containment.
- `rect_intersect`: in-place rectangle intersection, possibly anomalous if empty.
- `rect_merge`: in-place rectangle union/merge.
- `int_rect_difference`: computes outer-minus-inner into up to four rectangles.
- `PARALLELOGRAM_IS_RECT`: tests whether a parallelogram is axis-aligned rectangle.
- `INT_RECT_FROM_PARALLELOGRAM`: converts a rectangular parallelogram to integer rectangle using center-of-pixel rounding.

Integration:
- Includes `gxfixed.h`.
- Used by clipping, fill, and device geometry code.

Risk notes:
- Macros evaluate arguments multiple times and mutate targets; callers must avoid side-effect expressions.
- Empty/anomalous rectangle behavior is explicit and must be handled by callers.
