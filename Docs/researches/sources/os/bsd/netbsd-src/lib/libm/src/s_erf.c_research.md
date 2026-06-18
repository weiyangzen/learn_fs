# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_erf.c

Implements double `erf()` and `erfc()` using classic FDLIBM interval-specific rational approximations.

Key behavior: uses separate approximations for small `|x|`, near 1, medium-large erfc asymptotics, and saturation/underflow regions. Handles signed infinities and NaNs, and splits `x*x` via truncated `z` for exponent accuracy.

Important dependencies: `math_private.h`, `fabs`, and `__ieee754_exp`.

Notable risks: coefficients and interval thresholds are precision-critical; tiny constants intentionally force inexact/underflow behavior.
