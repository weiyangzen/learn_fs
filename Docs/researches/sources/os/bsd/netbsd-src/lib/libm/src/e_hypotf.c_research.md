# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_hypotf.c

Implements fdlibm kernel `__ieee754_hypotf(float, float)`.

Key behavior:
- Float version of `e_hypot.c`.
- Sorts magnitudes, handles extreme ratios, infinities, NaNs, and zero/subnormal inputs.
- Scales by powers of two to avoid overflow/underflow.
- Uses truncated high parts for compensated square summation before `sqrtf`.
