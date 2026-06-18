# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_tanpil.c

Implements `tanpil(long double x)`, computing `tan(pi*x)` directly. It uses a small internal `__kernel_tanpil()` wrapper that maps fractions around quarter/half periods into `__kernel_tanl()` calls with split `pi` constants.

Key behavior:
- Tiny inputs return a split `pi*x` result while preserving signed zero.
- For `|x| < 0.5`, evaluates tangent directly or through the `0.5 - x` identity.
- At half-integers, returns signed infinity via division by volatile zero.
- For `1 <= |x| < 2^63`, strips the integer part, tracks parity for signed zero/infinity, and evaluates the fractional part.
- For infinities/NaNs, returns NaN; for very large integers, returns signed zero based on the remaining representable parity.

Important dependencies: `math_private.h`, `__kernel_tanl`, `FFLOORL80`, `_2sumF`, and ld80 word macros.

Notable risks:
- Correct poles and signed zeros depend on exact half-integer detection.
