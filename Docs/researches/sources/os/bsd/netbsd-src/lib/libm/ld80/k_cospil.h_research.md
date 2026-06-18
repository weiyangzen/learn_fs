# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/k_cospil.h

This header defines inline `__kernel_cospil(long double x)` for ld80 `cos(pi*x)` after public range reduction.

It splits `x` with a float high part, multiplies by split double `pi_hi`/`pi_lo`, normalizes via `_2sumF`, and delegates to `__kernel_cosl`.

The use of float splitting differs from ld128’s double split and matches ld80 precision/performance needs. The includer must provide pi constants and the cosine kernel.
