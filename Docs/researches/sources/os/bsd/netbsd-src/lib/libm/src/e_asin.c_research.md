# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_asin.c

Implements fdlibm kernel `__ieee754_asin(double)`.

Key behavior:
- Handles `|x| >= 1`, returning signed `pi/2` for exactly `|x| == 1` and NaN outside domain.
- For `|x| < 0.5`, uses a rational approximation to `(asin(x)-x)/x^3`.
- For larger magnitudes, transforms through `sqrt((1-|x|)/2)`.
- Uses separate near-one and middle-range formulas to reduce cancellation.
- Restores sign at the end.
