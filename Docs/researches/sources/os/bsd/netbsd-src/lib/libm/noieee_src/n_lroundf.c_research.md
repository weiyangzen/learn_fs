# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_lroundf.c

Implements no-IEEE `lroundf(float)`.

Key behavior:
- Mirrors `n_lround.c` for float inputs.
- Uses `ceilf` on the absolute magnitude and applies the original sign.
- Rounds halfway cases away from zero.

Notable risk:
- Does not guard `long` overflow or NaN/infinity conversion.
