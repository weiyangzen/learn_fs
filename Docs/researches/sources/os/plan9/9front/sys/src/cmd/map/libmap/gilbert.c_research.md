# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/gilbert.c

Implements Gilbert projection. It maps the sphere onto a hemisphere using `tan(lat/2)` and half longitude, then presents the hemisphere orthographically.

The file includes a derivation comment: stereographic projection to plane, square root to half-plane, then inverse stereographic projection.
