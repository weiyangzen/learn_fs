# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_lgammal.c

This file provides the public long-double `lgammal(long double x)` wrapper.

It weak-aliases `lgammal` to `_lgammal`, declares the global `signgam`, and implements `lgammal(x)` by calling `lgammal_r(x, &signgam)`. It contains no approximation logic itself; all computation is delegated to the reentrant long-double implementation selected elsewhere.

Dependencies are `namespace.h`, `math.h`, `math_private.h`, weak alias support, and the external `signgam`.
