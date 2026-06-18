# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_hypot.c

Wrapper for double `hypot(x, y)`. It delegates to `__ieee754_hypot()` and reports overflow when the result is nonfinite but both inputs are finite.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `finite()`, and `__kernel_standard`.

Legacy overflow error code is `4`.
