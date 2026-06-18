# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_scalbnl.c

Implements long-double `scalbnl()`, `scalblnl()`, and `ldexpl()` aliases.

Key behavior: handles trivial zero/n==0, NaN/Inf, exponent overflow guards, denormal normalization, normal exponent rewrite, subnormal scaling, and signed overflow/underflow results.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `union ieee_ext_u`, `copysignl`, and format-specific underflow scale constants.

Notable risks: exponent-bound arithmetic is format-sensitive and only supports 64- or 113-bit mantissas.
