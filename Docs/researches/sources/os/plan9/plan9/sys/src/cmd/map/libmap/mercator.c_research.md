# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/mercator.c

Implements spherical Mercator and spheroidal Mercator.

Key functions:
- `mercator()` returns `Xmercator`.
- `Xmercator()` rejects latitudes outside `±80°`, maps longitude linearly and latitude via logarithmic Mercator formula.
- `sp_mercator()` returns `Xspmercator`.
- `Xspmercator()` applies an ellipsoid eccentricity correction using `ECC`.

Dependencies:
- `ECC` comes from `map.h`.
- Output longitude sign convention is `x = -wlon`.
