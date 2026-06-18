# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/conic.c

Read fully: 27 lines, 496 bytes. SHA-256 prefix: `335fab8b286b8617`.

Implements a simple conic projection. `conic(par)` returns cylindrical projection for near-equatorial parallels, otherwise stores the standard parallel and returns `Xconic`. The projection rejects points more than 80 degrees from the standard parallel, computes radius from tangent displacement, maps longitude scaled by sine of standard parallel, and returns clipped status when radius is large.

Dependencies: `Xcylindrical`, `deg2rad`.

Risk notes: static state holds only one standard parallel.
