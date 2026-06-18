# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nextafter.c

Implements double `nextafter(x,y)` by incrementing or decrementing the IEEE representation by one ulp.

Key behavior: returns NaN for NaN operands, returns `y` when equal, creates signed min-subnormal from zero, raises underflow/overflow through arithmetic, and aliases long-double variants when no long double exists.

Important dependencies: `math_private.h`, `EXTRACT_WORDS`, and `INSERT_WORDS`.

Notable risks: underflow flag forcing depends on evaluating `x*x` before final word insertion.
