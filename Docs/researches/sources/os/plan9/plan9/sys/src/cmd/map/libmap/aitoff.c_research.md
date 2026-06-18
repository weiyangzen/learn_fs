# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/aitoff.c

Read fully: 26 lines, 397 bytes. SHA-256 prefix: `fd7431e4ede851e2`.

Implements the Aitoff projection. `aitoff()` initializes a zero lat/lon pole and returns `Xaitoff`. The projection halves longitude, normalizes the place relative to `Xaitpole` and twist, applies azimuthal equal-area projection, then doubles x.

Dependencies: `copyplace`, `sincos`, `norm`, `latlon`, and `Xazequalarea`.

Risk notes: uses static shared projection state, so initialization is global rather than per-instance.
