# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_roundf.c

Implements no-IEEE `roundf(float)`.

Key behavior:
- Mirrors `round(double)` with `ceilf`.
- Handles signs by rounding the absolute magnitude then reapplying sign.
- Rounds halfway cases away from zero.
