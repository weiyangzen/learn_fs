# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/lagrange.c

Implements the Lagrange conformal projection as a `proj` factory returning `Xlagrange`.

Key flow:
- Copies the input `place`.
- Reflects southern latitudes into the northern hemisphere, then restores sign on output `y`.
- Uses `Xstereographic()` followed by complex square root and division helpers from libmap.
- Outputs `x = t2`, `y = -t1`.

Dependencies:
- `copyplace`, `Xstereographic`, `csqrt`, and `cdiv`.
- Always returns `1`; there is no explicit visibility rejection in this file.
