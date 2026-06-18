# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/occ.c

Detects and refines occultation/eclipse/transit contact times.

Key points:
- `occult` finds a sampled minimum angular separation between two objects, refines it at minute and sub-minute resolution, then records contact times.
- `set3pt` builds a quadratic interpolation model from three sampled points.
- `setpt` evaluates the interpolated active point.
- `pinorm` normalizes angular differences across wraparound.

Dependencies:
- Uses `dist`, `setime`, object functions, and object point arrays.

Notable behavior:
- Contact times `t1` through `t5` are initialized to sentinel `-100`.
