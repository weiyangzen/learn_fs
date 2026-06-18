# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_scalbnf.c

Implements float `scalbnf()`, `scalblnf()`, and `ldexpf()` aliases.

Key behavior: scales subnormals by `2^25`, directly rewrites exponent fields, and handles overflow/underflow with signed huge/tiny products.

Important dependencies: `namespace.h`, `math_private.h`, `copysignf`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: integer overflow guards use broad `n` thresholds.
