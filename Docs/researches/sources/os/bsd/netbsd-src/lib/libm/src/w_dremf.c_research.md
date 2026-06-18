# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_dremf.c

Implements legacy float `dremf(x, y)` as a direct call to `remainderf(x, y)`.

Important dependencies: `math.h` and `math_private.h`.

This is a compatibility shim with no independent arithmetic.
