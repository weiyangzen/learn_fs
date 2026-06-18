# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_cospil.c

This file implements ld80 `cospil(long double x)`.

It computes `cos(pi*x)` with explicit quadrant handling rather than multiplying by pi and calling `cosl` directly. For `|x| < 1`, it selects sine or cosine kernels based on fractional range. For `1 <= |x| < 2^63`, it uses `FFLOORL80` to split off the integer part, evaluates the fractional part, and flips sign based on integer parity.

For non-finite values it returns NaN. For very large finite values, representability determines parity: `|x| >= 2^64` is always an even integer, while `2^63 <= |x| < 2^64` checks the low mantissa bit.

The file uses ld80-specific bit extraction and `ENTERI`/`RETURNI` environment macros.
