# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_logb.c

Implements legacy double `logb()`, returning the floating-point exponent as a double.

Key behavior: returns `-inf` for zero through division by `fabs(x)`, returns `x*x` for Inf/NaN, returns `-1022` for subnormals, and normal exponent otherwise.

Important dependencies: `math_private.h`, `fabs`, and `EXTRACT_WORDS`.

Notable risks: comment notes `ilogb` is preferred; subnormal behavior returns minimum normal exponent rather than scanning.
