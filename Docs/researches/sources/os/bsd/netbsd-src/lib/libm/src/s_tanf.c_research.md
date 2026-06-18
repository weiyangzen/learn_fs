# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanf.c

Implements single-precision `tanf()`, mirroring `s_tan.c`. It calls `__kernel_tanf()` for `|x| <= pi/4`, otherwise reduces with `__ieee754_rem_pio2f()` and passes the quadrant parity to the tangent kernel.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `GET_FLOAT_WORD`, `__kernel_tanf`, and `__ieee754_rem_pio2f`.

Special cases: infinities and NaNs return `x - x`. Thresholds are float bit constants, so behavior is tied to IEEE-754 single precision.
