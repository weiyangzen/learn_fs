# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_isinff.c

Implements float `isinff()` by checking the absolute bit pattern against infinity.

Key behavior: returns 1 for positive or negative infinity and 0 otherwise.

Important dependencies: `math_private.h` and `GET_FLOAT_WORD`.

Notable risks: assumes IEEE single-precision layout.
