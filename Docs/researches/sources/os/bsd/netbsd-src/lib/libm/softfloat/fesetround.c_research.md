# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fesetround.c

Implements `fesetround`.

Key behavior:
- Converts the fenv rounding mode with `__FPR`.
- Sets the softfloat rounding mode through `fpsetround`.
- Always returns 0.
