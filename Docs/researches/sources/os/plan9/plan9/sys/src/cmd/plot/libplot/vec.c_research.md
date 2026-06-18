# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/vec.c

Draws a clipped vector from current position to a target point.

Key responsibilities:
- Converts current and target plot coordinates to screen coordinates.
- Updates current plot position to the target.
- Performs Cohen-Sutherland-style clipping against `clipmin/clipmax`.
- Calls backend `m_vector()` for visible clipped segments.

Important behavior:
- Drops vectors with coordinates beyond `BIGINT`.
- Even fully clipped segments still update the logical current point.

Notable risks:
- Integer divisions in clipping branches assume nonzero denominators implied by the selected clip edge.
