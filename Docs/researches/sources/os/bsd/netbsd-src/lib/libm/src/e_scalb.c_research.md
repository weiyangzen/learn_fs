# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_scalb.c

This file implements legacy double `__ieee754_scalb`.

With `_SCALB_INT`, it directly delegates to `scalbn(x, fn)`. Otherwise, the exponent argument is a double: NaNs propagate, infinite exponents produce multiply/divide behavior, non-integral exponents produce NaN, large exponents are clamped to `+/-65000`, and finite integral exponents call `scalbn`.

The file exists for legacy test-suite compatibility; comments recommend `scalbn` instead. Dependencies include `isnan`, `finite`, `rint`, and `scalbn`.
