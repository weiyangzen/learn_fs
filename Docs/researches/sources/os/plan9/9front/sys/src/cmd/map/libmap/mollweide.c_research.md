# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/mollweide.c

Implements Mollweide projection. `Xmollweide()` solves `2z + sin(2z) = PI*sin(lat)` by Newton iteration, then maps y to `sin(z)` and x to scaled longitude times `cos(z)`. It skips iteration near the poles.

`mollweide()` returns `Xmollweide()`.
