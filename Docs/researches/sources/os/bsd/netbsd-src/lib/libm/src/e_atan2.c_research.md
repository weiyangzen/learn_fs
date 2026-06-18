# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_atan2.c

Implements fdlibm kernel `__ieee754_atan2(double y, double x)`.

Key behavior:
- Handles NaNs, signed zeros, zero `x`, infinities, and all quadrant cases.
- Fast-paths `x == 1.0` to `atan(y)`.
- Builds quadrant index from the signs of `x` and `y`.
- Avoids unsafe division when `|y/x|` is extremely large or small.
- Uses `atan(fabs(y/x))` for the core angle.
