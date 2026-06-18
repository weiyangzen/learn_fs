# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_j0.c

Implements fdlibm kernels `__ieee754_j0(double)` and `__ieee754_y0(double)` for Bessel functions of order zero.

Key behavior:
- `j0` is even; small inputs use polynomial/rational approximation near 1.
- For `|x| >= 2`, computes asymptotic forms using `sin`, `cos`, `sqrt`, and helper rational functions `pzero`/`qzero`.
- Uses cancellation-avoidance identities based on `cos(2x)`.
- `y0` handles zero as `-inf`, negative inputs as NaN, infinities as zero, and small positive inputs with `log(x)`.
- `pzero` and `qzero` select coefficient tables by input range.

This file contains substantial approximation tables for the large-argument asymptotic expansions.
