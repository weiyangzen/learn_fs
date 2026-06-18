# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_acos.c

Implements fdlibm kernel `__ieee754_acos(double)`.

Key behavior:
- Handles `|x| == 1`, `|x| > 1`, and NaN through bit inspection.
- For `|x| < 0.5`, computes `pi/2 - asin(x)` using a rational approximation.
- For `x < -0.5`, transforms to `pi - 2*asin(sqrt((1-|x|)/2))`.
- For `x > 0.5`, computes `2*asin(sqrt((1-x)/2))` with a split square-root correction.
- Uses `__ieee754_sqrt`.
