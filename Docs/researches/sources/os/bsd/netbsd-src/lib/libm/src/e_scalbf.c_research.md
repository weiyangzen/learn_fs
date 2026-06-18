# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_scalbf.c

This file implements the float legacy scaling function `__ieee754_scalbf`.

It mirrors `e_scalb.c`: `_SCALB_INT` builds delegate to `scalbnf`; otherwise NaNs propagate, infinite exponent arguments produce multiply/divide behavior, non-integral exponent arguments return NaN, large exponents clamp to `+/-65000`, and finite integral exponents call `scalbnf`.

Dependencies include `isnanf`, `finitef`, `rintf`, and `scalbnf`.
