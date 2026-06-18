# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_pow.c

Wrapper for double `pow(x, y)`. It delegates to `__ieee754_pow()` and, outside IEEE mode, classifies NaN-to-zero, zero-to-zero, zero-to-negative, negative-base non-integer, overflow, and underflow cases.

Important dependencies: `math.h`, `math_private.h`, `isnan()`, `finite()`, and `__kernel_standard`.

Legacy error codes include `42`, `20`, `23`, `24`, `21`, and `22`, depending on the condition.
