# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/line.c

Draws thick lines, endpoints, and arrowheads.

Key functions:
- `membrush`, `discend`: create and use circular endpoint masks.
- `arrowend`: computes arrowhead polygon points from line direction.
- `_memimageline`: main line rasterization routine.
- `memimageline`: public wrapper using destination clipr.
- `memlineendsize`, `memlinebbox`: bounding-box helpers for layer clipping.

Important behavior:
- Fast path for axis-aligned square-ended lines draws a rectangle.
- General thick lines are converted into polygons and filled through `_memfillpolysc`.
- Disc and arrow endpoints are drawn as masks/polygons.
- Uses `icossin2` for scaled vector direction.
