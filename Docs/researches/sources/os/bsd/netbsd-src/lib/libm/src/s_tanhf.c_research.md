# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanhf.c

Implements single-precision `tanhf()`. It follows the double implementation with float thresholds and calls `expm1f()`/`fabsf()` for stable hyperbolic tangent formulas.

Important dependencies: `math.h`, `math_private.h`, `GET_FLOAT_WORD`, `fabsf()`, and `expm1f()`.

Special cases: infinities produce signed one, NaNs propagate, tiny values return `x*(1+x)`, and large finite values return `1 - tiny` with the original sign.
