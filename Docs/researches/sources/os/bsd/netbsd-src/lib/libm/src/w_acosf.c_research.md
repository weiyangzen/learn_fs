# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_acosf.c

Wrapper for float `acosf()`. It returns `__ieee754_acosf(x)` in IEEE mode and otherwise converts `|x| > 1` domain errors to `__kernel_standard(..., 101)`.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `__ieee754_acosf`, `fabsf()`, and `isnanf()`.

This file is the float analogue of `w_acos.c`.
