# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_significandf.c

Implements float `significandf(x)`.

Key behavior: computes `__ieee754_scalbf(x, -ilogbf(x))`.

Important dependencies: `math_private.h`, `__ieee754_scalbf`, and `ilogbf`.

Notable risks: same special-value behavior caveats as double `significand()`.
