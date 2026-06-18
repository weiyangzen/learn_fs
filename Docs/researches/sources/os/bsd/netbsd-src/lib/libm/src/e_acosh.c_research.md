# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_acosh.c

Implements fdlibm kernel `__ieee754_acosh(double)`.

Key behavior:
- Returns NaN for `x < 1`.
- Returns zero for `x == 1`.
- For huge `x`, returns `log(x) + ln2`.
- For `x > 2`, uses `log(2x - 1/(x + sqrt(x*x-1)))`.
- For `1 < x < 2`, uses `log1p(t + sqrt(2t+t*t))` with `t = x - 1`.
