# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_atanhf.c

Implements fdlibm kernel `__ieee754_atanhf(float)`.

Key behavior:
- Float version of `e_atanh.c`.
- Handles out-of-domain, exact `|x| == 1`, tiny, small, and large in-domain cases.
- Uses `log1pf` formulas and restores sign.
