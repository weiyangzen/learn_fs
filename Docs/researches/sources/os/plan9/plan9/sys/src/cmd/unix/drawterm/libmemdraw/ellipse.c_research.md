# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/ellipse.c

Rasterizes filled and stroked ellipses.

Key functions:
- `newstate`, `step`: integer ellipse stepping state based on residual error.
- `memellipse`: main ellipse drawing routine.
- `bellipse`: draws very thick skinny ellipses by brushing with a circular mask.
- `erect`, `epoint`, `eline`: draw horizontal spans, brushed points, and brushed lines.

Important behavior:
- Supports filled ellipses when thickness `t < 0`.
- For normal thickness, fills between outer and inner ellipses.
- Uses `memdraw` with `memopaque` masks and source point adjustment.
