# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/harrison.c

Read fully: 40 lines, 708 bytes. SHA-256 prefix: `b8d06137690124ef`.

Implements Harrison projection with view/object geometry parameters `r` and `alpha`. `harrison()` computes unit/view constants, rejects invalid geometry, and returns `Xharrison`. The projection maps a spherical point to 3D components, computes perspective divisor, rejects near/behind cases, maps x/y, and clips by sign and radius.

Risk notes: returns both `0` and `-1` for different rejection/clipping cases. Static parameters are global to the projection.
