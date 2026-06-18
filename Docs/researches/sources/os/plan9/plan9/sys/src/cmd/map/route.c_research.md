# File Research: sources/os/plan9/plan9/sys/src/cmd/map/route.c

Implements `route`, a helper that computes `map -o` orientation options for a great-circle route between two lat/lon points.

Behavior:
- Usage: `route [-t] [-i] lat lon lat lon`.
- Without `-t`, prints suggested `-o` and `-w` options to orient a standard projection so the two points lie on the equator around the prime meridian.
- With `-t`, prints intermediate great-circle track coordinates suitable for `map -t`.
- `-i` flips the route top-to-bottom via `inv`.

Key functions:
- `dorot()` wraps `deg2rad` and a transform callback.
- `rotate()` applies `normalize`.
- `rinvert()` applies `invert`.
- `doroute()` derives route pole and twist through repeated orientation/rotation steps.

Dependencies:
- Uses `orient`, `normalize`, and `invert` from `zcoord.c`.
