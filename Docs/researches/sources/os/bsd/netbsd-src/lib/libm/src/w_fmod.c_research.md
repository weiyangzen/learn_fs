# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_fmod.c

Wrapper for double `fmod(x, y)`. It calls `__ieee754_fmod()` and maps `y == 0` to `__kernel_standard(x, y, 27)` outside IEEE mode, unless either argument is NaN.

Important dependencies: `math.h`, `math_private.h`, `isnan()`, and `__ieee754_fmod`.

Also aliases `fmodl` to double `fmod` when long double is unavailable.
