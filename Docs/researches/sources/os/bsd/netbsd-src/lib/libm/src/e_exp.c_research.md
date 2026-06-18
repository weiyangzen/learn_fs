# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_exp.c

Implements fdlibm kernel `__ieee754_exp(double)`.

Key behavior:
- Handles NaN, positive/negative infinity, overflow, and underflow thresholds.
- Reduces input to `k*ln2 + r`, with split high/low `ln2` constants.
- Uses a degree-5 polynomial approximation for the primary interval.
- Reconstructs by directly adjusting the exponent of the computed significand.
- Handles subnormal scaling through a `2^-1000` multiplier.
