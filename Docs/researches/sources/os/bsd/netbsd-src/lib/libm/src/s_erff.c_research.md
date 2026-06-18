# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_erff.c

Implements float `erff()` and `erfcf()` as a float conversion of the FDLIBM double algorithms.

Key behavior: uses float coefficient sets for the same approximation intervals as `s_erf.c`; handles Inf/NaN, small inputs, saturation, and erfc underflow.

Important dependencies: `math_private.h`, `fabsf`, and `__ieee754_expf`.

Notable risks: precision and exception behavior depend on carefully rounded float coefficients and truncating `z` with word masks.
