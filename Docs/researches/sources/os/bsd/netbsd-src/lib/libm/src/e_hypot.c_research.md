# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_hypot.c

Implements fdlibm kernel `__ieee754_hypot(double, double)`.

Key behavior:
- Orders inputs by magnitude and works with absolute values.
- Returns early when the ratio is so large that the smaller input cannot affect the result.
- Handles infinities and NaNs carefully, including signaling NaN quieting.
- Scales very large and very small inputs to avoid overflow/underflow.
- Uses compensated split products before `sqrt` to keep error below 1 ulp.
- Scales the result back if needed.
