# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanpi.c

Implements double-precision `tanpi(x)`, computing `tan(pi*x)` with direct period-aware reduction. It uses split `pi_hi`/`pi_lo` constants for small values, handles fractions in `[0, 1)` without general argument reduction, strips integer parts for `1 <= |x| < 2^52`, and treats larger finite values as integral.

Important dependencies: `namespace.h`, `<float.h>`, `math.h`, `math_private.h`, `_2sumF`, `FFLOOR`, word extraction/insertion macros, `__kernel_tan`, and `copysign()`.

Special cases include signed zeros at integers, signed infinities at half-integers using division by volatile zero, `+-1` at quarter offsets, and NaN for Inf/NaN.
