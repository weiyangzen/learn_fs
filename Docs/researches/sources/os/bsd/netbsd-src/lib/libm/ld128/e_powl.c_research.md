# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/e_powl.c

This file implements `powl(long double x, long double y)` for 128-bit long double.

It follows the classic fdlibm method: compute `log2(abs(x))` in high/low pieces, multiply by `y` with split arithmetic, then compute `2**z` through polynomial approximation and exponent scaling. It contains extensive special-case handling for zero, infinities, NaNs, `x == +/-1`, integer exponents for negative bases, square roots for `y == 0.5`, overflow, and underflow.

For negative bases it determines whether `y` is an odd integer, even integer, or non-integer. Non-integer powers of negative finite values return NaN; odd integer exponents preserve sign.

The code uses quad word access through `ieee_quad_shape_type`, explicit mantissa masking to split high/low parts, and polynomial coefficient arrays for logarithm and exponential approximations.
