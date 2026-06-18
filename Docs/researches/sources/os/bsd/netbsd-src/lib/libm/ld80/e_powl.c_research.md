# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/e_powl.c

This file implements ld80 `powl(long double x, long double y)` using Stephen Moshier/Cephes-style algorithms.

It includes helper polynomial evaluators `__polevll()` and `__p1evll()`, log tables `A[]`/`B[]`, and exponential polynomial `R[]`. The main path computes `x**y` as `2**(y*log2(x))`, using a table of `2^(-i/32)` and pseudo-extended arithmetic.

Special cases cover zeros, infinities, NaNs, negative bases, integer exponents, and huge positive/negative `y`. For integer `y` and integral `x` with `|y| < 32768`, it uses `powil()` exponentiation by squaring.

The implementation uses file-scope temporaries and is less reentrant in style than newer kernels, but all state is internal to the function execution.
