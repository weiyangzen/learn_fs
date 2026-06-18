# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_atan2f.c

Implements fdlibm kernel `__ieee754_atan2f(float y, float x)`.

Key behavior:
- Float version of `e_atan2.c`.
- Handles NaNs, signed zeros, infinities, and quadrants by bit inspection.
- Uses `atanf(fabsf(y/x))` when division is safe.
- Uses small `tiny` additions/subtractions to trigger inexact in boundary cases.
