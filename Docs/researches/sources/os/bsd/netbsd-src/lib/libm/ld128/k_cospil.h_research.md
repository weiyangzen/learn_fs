# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/k_cospil.h

This header defines inline `__kernel_cospil(long double x)`, a helper for computing `cos(pi*x)` after high-level range reduction.

It splits `x` into a double-precision high part and long-double residual, multiplies both by split `pi_hi`/`pi_lo`, renormalizes with `_2sumF`, and calls `__kernel_cosl(hi, lo)`.

The header expects `pi_hi`, `pi_lo`, `_2sumF`, and `__kernel_cosl` to be available from the including file. It avoids redoing public-level quadrant reduction and focuses only on accurate multiplication by pi for small reduced inputs.
