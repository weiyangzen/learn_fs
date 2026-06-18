# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_pow.c

This file implements `__ieee754_pow(double x, double y)`.

The algorithm computes `log2(|x|)` in high/low pieces, multiplies by `y` using split arithmetic, checks overflow/underflow in the resulting exponent, and evaluates `2**z` with polynomial approximation and exponent adjustment. It includes extensive special-case handling for zero exponents, `x == 1`, NaNs, infinities, zero bases, negative bases, integer parity of `y`, square-root shortcut for `y == 0.5`, and huge exponents.

For negative finite bases, it distinguishes non-integer, odd integer, and even integer exponents to decide NaN and result sign. Dependencies include `fabs`, `scalbn`, `__ieee754_sqrt`, and direct IEEE double word operations.
