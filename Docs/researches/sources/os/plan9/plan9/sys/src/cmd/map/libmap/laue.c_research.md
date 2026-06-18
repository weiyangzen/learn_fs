# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/laue.c

Implements the Laue projection.

Key behavior:
- `laue()` returns `Xlaue`.
- `Xlaue()` only plots northern points above roughly `45°`.
- Computes `r = tan(PI - 2*lat)`.
- Rejects points when `r > 3`.
- Outputs circular coordinates using longitude sine/cosine: `x = -r*sin(lon)`, `y = -r*cos(lon)`.

This is a small bounded polar-style projection with hard cutoff behavior.
