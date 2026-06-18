# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/zcoord.c

Provides core spherical coordinate utilities for the map library.

Key functions:
- `orient(lat, lon, theta)` sets global map pole/twist and inverse transform.
- `latlon()` fills a `struct place` from degrees.
- `deg2rad()` normalizes degrees and fills radians/sin/cos.
- `normalize()` and `invert()` apply global forward/inverse orientation.
- `norm()` rotates a `struct place` into a pole/twist coordinate frame.
- `sincos()`, `copyplace()`, `printp()`, and a local `tan()` helper.

Behavior notes:
- `cirmod()` normalizes degrees into `[-180, 180)`.
- `latlon()` folds latitudes outside `±90°` and shifts longitude by `180°`.
- `norm()` handles the trivial north-pole orientation as a special case, then keeps longitude within `[-PI, PI]`.
- This file owns global orientation state used by `map.c`, `route.c`, and projections.
