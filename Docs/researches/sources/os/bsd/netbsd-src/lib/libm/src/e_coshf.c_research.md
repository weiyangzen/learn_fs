# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_coshf.c

Implements fdlibm kernel `__ieee754_coshf(float)`.

Key behavior:
- Float version of `e_cosh.c`.
- Handles NaN/infinity, tiny, medium, large, near-overflow, and overflow ranges.
- Uses `expm1f` and `__ieee754_expf`.
