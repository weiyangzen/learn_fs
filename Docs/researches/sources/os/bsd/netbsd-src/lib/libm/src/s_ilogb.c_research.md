# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_ilogb.c

Implements double `ilogb()`, returning the unbiased binary exponent as an integer.

Key behavior: raises `FE_INVALID` and returns `FP_ILOGB0` for zero; scans subnormal significands; returns exponent for normal values; raises invalid and returns `FP_ILOGBNAN` or `INT_MAX` for NaN/Inf.

Important dependencies: `fenv.h`, `math_private.h`, `isnan`, and word access macros.

Notable risks: subnormal loops are bit-layout dependent.
