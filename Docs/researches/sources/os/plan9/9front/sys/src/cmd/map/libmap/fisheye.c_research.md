# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/fisheye.c

Implements a refractive fisheye projection parameterized by refractive index `n`. It computes a transformed radial value from latitude, rejects values near the asin limit, and maps by longitude sine/cosine.

`fisheye()` rejects parameters below 0.1.
