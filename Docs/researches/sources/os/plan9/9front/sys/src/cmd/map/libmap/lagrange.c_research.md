# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/lagrange.c

Implements Lagrange projection. It mirrors southern latitudes to the north, applies stereographic projection, complex square root and division transforms, then restores y sign for southern latitudes.

`lagrange()` returns `Xlagrange()`.
