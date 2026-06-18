# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/perspective.c

Implements perspective, stereographic, and gnomonic projections through shared `viewpt` state.

Key behavior:
- `perspective(radius)` returns orthographic for very large radius, rejects radius near 1, otherwise uses `Xperspective()`.
- `Xperspective()` computes radial scale from viewpoint and latitude, rejects singular/too-large points, and returns hidden/visible status.
- `Xstereographic()` temporarily sets `viewpt = -1` for use by other conformal projections.
- `stereographic()` and `gnomonic()` set `viewpt` to -1 and 0 respectively.
- `plimb()` generates the visible limb, delegating to `olimb()` for orthographic-like cases.

This shared static `viewpt` means only one such projection can be active safely at a time.
