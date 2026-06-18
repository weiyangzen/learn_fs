# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_cosh.c

Implements fdlibm kernel `__ieee754_cosh(double)`.

Key behavior:
- Uses `|x|` because cosh is even.
- For small `|x|`, uses `expm1` to compute `1 + expm1(x)^2/(2*exp(x))`.
- For medium `|x|`, computes `(exp(x) + 1/exp(x))/2`.
- For larger safe values, returns `exp(|x|)/2`.
- Near overflow threshold, computes `exp(x/2)/2 * exp(x/2)`.
- Overflows through `huge*huge` past the threshold.
