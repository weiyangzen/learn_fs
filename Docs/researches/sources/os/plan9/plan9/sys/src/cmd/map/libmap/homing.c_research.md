# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/homing.c

Implements the `mecca` and `homing` map projections plus their limb iterators. Both projections use a configured standard parallel `p0` and compute an azimuth/distance from each input `struct place` to that reference.

Key functions:
- `mecca(double par)` validates `|par| <= 80`, initializes `p0`, and returns `Xmecca`.
- `homing(double par)` does the same and returns `Xhoming`.
- `azimuth()` computes spherical azimuth and angular distance using trigonometric clamps to avoid domain drift.
- `hlimb()` traces the visible limb for homing.
- `mlimb()` traces the Mecca projection boundary unless the standard parallel is effectively equatorial.

Behavior notes:
- Projection return values follow libmap convention: `1` drawable, `0` wrong sheet/hidden, `-1` unplottable.
- `first` is global, not static, and is reset by both projection factories for limb iteration.
- `Xmecca` rejects extreme `y` values and hides the far hemisphere using `rad.c < 0`.
- `Xhoming` uses azimuthal distance components and hides points where `place->wlon.c < 0`.
