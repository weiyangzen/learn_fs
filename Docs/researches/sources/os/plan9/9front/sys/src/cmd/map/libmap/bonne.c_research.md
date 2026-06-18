# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/bonne.c

Implements Bonne projection. `bonne()` falls back to sinusoidal projection for near-equatorial standard parallels, otherwise stores the standard parallel and `r0`. `Xbonne()` computes radial distance from the standard parallel and angular displacement, with special handling near the pole/zero-radius case.

It returns the shared `Xsinusoidal` function for the degenerate case.
