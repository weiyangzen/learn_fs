# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_isnanf.c

Implements float `isnanf()` with branchless absolute-bit comparison.

Key behavior: returns 1 when the absolute representation is greater than infinity.

Important dependencies: `math_private.h` and `GET_FLOAT_WORD`.

Notable risks: relies on IEEE float encoding.
