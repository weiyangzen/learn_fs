# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_ilogbf.c

Implements float `ilogbf()`.

Key behavior: raises invalid for zero, NaN, and infinity; scans subnormals to compute exponent; returns normal exponent from the float exponent field.

Important dependencies: `fenv.h`, `math_private.h`, `GET_FLOAT_WORD`, and `isnan`.

Notable risks: exception behavior depends on platform fenv availability.
