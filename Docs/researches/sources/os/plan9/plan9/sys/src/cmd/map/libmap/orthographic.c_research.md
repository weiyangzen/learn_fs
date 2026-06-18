# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/orthographic.c

Implements orthographic projection and limb tracing.

Key functions:
- `orthographic()` returns `Xorthographic`.
- `Xorthographic()` maps visible hemisphere coordinates with `x = -cos(lat)*sin(lon)`, `y = -cos(lat)*cos(lon)`.
- Returns `0` for southern normalized latitudes and `1` otherwise.
- `olimb()` iterates the equatorial limb from longitude `-180` to `180`.

Notes:
- `olimb()` uses a static `first` state reset after completion.
- The projection is also reused by `perspective()` for very large viewpoint radii.
