# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cbrtf.c

This file implements public float `cbrtf(float x)`.

It preserves sign, handles NaN/Inf and zero, creates a rough cube-root estimate from float exponent bits, scales subnormals by `2**24`, and refines with the same rational approximation family used in the double version. The float version stops after the 23-bit refinement and restores the sign.

Dependencies are `math_private.h` float word macros and local constants.
