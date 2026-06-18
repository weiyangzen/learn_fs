# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/mollweide.c

Implements the Mollweide equal-area projection.

Key behavior:
- `mollweide()` returns `Xmollweide`.
- Uses Newton iteration to solve `2z + sin(2z) = PI*sin(lat)`.
- Skips iteration near the poles.
- Outputs `y = sin(z)` and `x = -(2/PI)*cos(z)*lon`.
- Always returns `1`; no explicit clipping or sheet rejection is performed.
