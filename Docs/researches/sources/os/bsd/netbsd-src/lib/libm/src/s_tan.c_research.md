# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tan.c

Implements double-precision `tan()`. For `|x| <= pi/4`, it calls `__kernel_tan(x, 0, 1)` directly. For finite larger arguments, it reduces by `__ieee754_rem_pio2()` and selects tangent or reciprocal-tangent behavior through the kernel `iy` sign argument.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `GET_HIGH_WORD`, `__kernel_tan`, and `__ieee754_rem_pio2`.

Special cases: infinities and NaNs return `x - x`, producing NaN. Accuracy and exception behavior depend on fdlibm argument reduction and kernel tangent semantics.
