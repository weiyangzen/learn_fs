# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_fmodf.c

Implements fdlibm kernel `__ieee754_fmodf(float, float)`.

Key behavior:
- Float version of exact shift/subtract `fmod`.
- Handles zero divisor, non-finite dividend, NaN divisor, `|x| < |y|`, and equality.
- Normalizes subnormal values, reduces significands, then restores sign and exponent.
