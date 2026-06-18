# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_rintl.c

Implements long-double `rintl()` using a large shift addition/subtraction trick.

Key behavior: returns Inf/NaN as `x+x`, leaves already integral values unchanged, rounds using current mode, and fixes signed zero for small magnitudes.

Important dependencies: `<machine/ieee.h>`, `math_private.h`, `GET_EXPSIGN`, and long-double shift constants.

Notable risks: source explicitly requires intermediate results to be evaluated in long-double precision; i386-style excess/insufficient precision can break results.
