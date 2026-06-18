# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_j1.c

Implements fdlibm kernels `__ieee754_j1(double)` and `__ieee754_y1(double)` for Bessel functions of order one.

Key behavior:
- `j1` is odd; small inputs return approximately `x/2` with rational correction.
- For `|x| >= 2`, uses asymptotic forms with `sin`, `cos`, `sqrt`, and helper functions `pone`/`qone`.
- Uses cancellation-avoidance identities based on `cos(2x)`.
- `y1` handles zero as `-inf`, negative inputs as NaN, infinities as zero, tiny positives as `-2/(pi*x)`, and ordinary positives with a rational/log expression.
- `pone` and `qone` select range-specific coefficient tables for asymptotic corrections.
