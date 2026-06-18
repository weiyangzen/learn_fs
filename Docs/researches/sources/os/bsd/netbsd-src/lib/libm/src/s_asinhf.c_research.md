# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_asinhf.c

This file implements public float `asinhf(float x)`.

It mirrors the double `asinh` implementation with float thresholds and constants: tiny return, large `logf(|x|)+ln2`, medium-large stable logarithm, and small-normal `log1pf` form. It preserves the sign at the end.

Dependencies include `__ieee754_logf`, `__ieee754_sqrtf`, `log1pf`, `fabsf`, and float word extraction.
