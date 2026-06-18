# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfillts.h

Template header that generates adjusted slanted-trapezoid filling helpers.

Key behavior:
- Defines `TEMPLATE_slant_into_trapezoids(const line_list *, const active_line *, const active_line *, fixed, fixed)`.
- Models fill adjustment as dragging a square around the trapezoid boundary, not simply expanding corners.
- Distinguishes top-wider, bottom-wider, and generally slanted cases.
- Uses direct rectangle fills for one-pixel adjustment caps where possible.
- Delegates complex slanted cases to `fill_slant_adjust`.
- Uses `loop_fill_trap_np` for clipped trapezoid emission.

Template parameters:
- `FILL_DIRECT`
- `TEMPLATE_slant_into_trapezoids`

Dependencies:
- Included by `gxfill.c` after `fill_slant_adjust` and `loop_fill_trap_np` are defined.

Research notes:
- This is a geometry-correctness helper for fill-adjusted paths.
- It avoids over-simplified expansion that would distort slanted trapezoid edges.
