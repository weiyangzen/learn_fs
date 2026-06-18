# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetexcept.c

Implements `fegetexcept`.

Key behavior:
- Returns the currently enabled floating-point exception mask.
- Translates from softfloat mask bits to fenv bits with `__FEE(fpgetmask())`.
