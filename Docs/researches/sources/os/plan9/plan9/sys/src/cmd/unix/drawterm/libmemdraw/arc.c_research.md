# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/arc.c

Draws elliptical arc sectors using temporary masks.

Key function:
- `memarc`: creates a wedge mask for angular bounds, creates a full ellipse mask, intersects them, then draws source through the resulting mask.

Important behavior:
- Handles negative radii by absolute value.
- Converts Plan 9 screen-coordinate orientation by negating angles.
- If the arc span is at least 360 degrees, delegates to `memellipse`.
- Uses `icossin`, `memfillpoly`, `memellipse`, and `memimagedraw`.
