# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_logbf.c

Implements float `logbf()`.

Key behavior: returns `-inf` for zero, propagates Inf/NaN via `x*x`, returns `-126` for subnormals, and normal exponent otherwise.

Important dependencies: `math_private.h`, `fabsf`, and `GET_FLOAT_WORD`.

Notable risks: IEEE float encoding assumed.
