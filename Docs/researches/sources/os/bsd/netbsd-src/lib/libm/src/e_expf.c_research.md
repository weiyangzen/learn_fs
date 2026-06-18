# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_expf.c

Implements fdlibm kernel `__ieee754_expf(float)`.

Key behavior:
- Float version of `e_exp.c`.
- Uses float thresholds and split `ln2` constants.
- Adjusts float exponent bits directly for scaling.
- Handles subnormal scaling through a `2^-100` multiplier.
