# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_atanh.c

Implements fdlibm kernel `__ieee754_atanh(double)`.

Key behavior:
- Returns NaN for `|x| > 1`.
- Returns signed infinity for `|x| == 1`.
- Returns `x` for tiny inputs while triggering inexact for nonzero values.
- Uses `0.5*log1p(2x + 2x*x/(1-x))` for `|x| < 0.5`.
- Uses `0.5*log1p(2x/(1-x))` for larger in-domain inputs.
- Restores the original sign.
