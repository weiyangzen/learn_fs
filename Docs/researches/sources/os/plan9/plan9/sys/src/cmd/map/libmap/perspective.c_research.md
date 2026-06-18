# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/perspective.c

Implements perspective-family projections.

Key functions:
- `perspective(double radius)` returns `Xorthographic` for huge radius, rejects radius near `1`, otherwise returns `Xperspective`.
- `stereographic()` sets `viewpt = -1`.
- `gnomonic()` sets `viewpt = 0`.
- `Xstereographic()` temporarily forces `viewpt = -1` for callers needing stereographic math.
- `plimb()` traces the visible boundary, delegating to `olimb()` for orthographic.

Behavior notes:
- `Xperspective()` computes radial scale from `viewpt` and normalized latitude.
- Rejects overly large projected radii.
- Returns `0` for hidden side based on `viewpt`.
- The first guard contains suspicious old C expression shape: `fabs(place->nlat.s<=viewpt+.01)` applies `fabs` to a comparison result, but this is source behavior as read.
