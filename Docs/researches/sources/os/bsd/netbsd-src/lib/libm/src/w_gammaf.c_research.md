# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_gammaf.c

Implements float `gammaf(x)` through `__ieee754_lgammaf_r(x, &signgam)`. In non-IEEE modes, finite inputs producing nonfinite results are mapped to pole or overflow errors.

Important dependencies: `math.h`, `math_private.h`, `signgam`, `floorf()`, `finitef()`, and `__kernel_standard`.

Error codes: `141` for poles and `140` for overflow.
