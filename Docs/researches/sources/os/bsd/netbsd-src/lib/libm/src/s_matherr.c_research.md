# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_matherr.c

Defines default legacy `matherr()` hook.

Key behavior: returns 0 for all normal exception records and also returns 0 when `arg1` is NaN.

Important dependencies: `math.h`, `math_private.h`, and `struct exception`.

Notable risks: this is legacy SVID-style behavior and is mostly a compatibility hook.
