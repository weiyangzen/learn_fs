# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/e_lgammal_r.c

This file implements `lgammal_r(long double x, int *signgamp)` for IEEE quad-style 128-bit long double.

It uses Sun fdlibm structure adapted to ld128. It handles NaN/Inf, zero, tiny inputs, negative integers, and negative non-integers through the reflection formula. The helper `sin_pil()` computes `sin(pi*x)` with octant reduction using 112-bit scaling constants and calls `__kernel_sinl`/`__kernel_cosl`.

For positive values, the implementation splits the domain into small intervals around 1, 2, and the lgamma minimum `tc`, then uses separate polynomial/rational approximations. For `2 <= x < 8`, it reduces by recurrence and adds logs of products. For large `x`, it uses a Stirling-series approximation.

The sign of gamma is reported through `signgamp`; singularities return division by volatile zero to raise the expected floating exception.
