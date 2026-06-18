# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_fmod.c

Implements fdlibm kernel `__ieee754_fmod(double, double)`.

Key behavior:
- Returns NaN for zero divisor, non-finite dividend, or NaN divisor.
- Returns `x` when `|x| < |y|` and signed zero when `|x| == |y|`.
- Computes exponents for normal and subnormal operands.
- Normalizes significands and performs exact fixed-point shift/subtract reduction.
- Converts the remainder back to floating point and restores the dividend sign.
- Aliases `__ieee754_fmodl` to this function when long double is unavailable.
