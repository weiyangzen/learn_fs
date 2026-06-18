# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/sinusoidal.c

Implements sinusoidal projection.

Key functions:
- `sinusoidal()` returns `Xsinusoidal`.
- `Xsinusoidal()` maps `x = -lon*cos(lat)`, `y = lat`.
- Always returns `1`.

This is a minimal equal-area projection implementation relying entirely on cached trigonometric values in `struct place`.
