# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_significand.c

Implements double `significand(x)` for IEEE 754-1985 test compatibility.

Key behavior: computes `scalb(x, -ilogb(x))` through internal `__ieee754_scalb`.

Important dependencies: `math_private.h`, `__ieee754_scalb`, and `ilogb`.

Notable risks: behavior for zero/NaN/Inf follows `ilogb` and `scalb` interactions.
