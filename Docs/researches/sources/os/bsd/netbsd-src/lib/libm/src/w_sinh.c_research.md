# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_sinh.c

Wrapper for double `sinh()`. It delegates to `__ieee754_sinh()` and reports overflow when a finite input produces a nonfinite result outside IEEE mode.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `finite()`, and `__kernel_standard`.

Legacy overflow error code is `25`.
