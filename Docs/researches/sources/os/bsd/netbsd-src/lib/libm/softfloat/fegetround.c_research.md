# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetround.c

Implements `fegetround`.

Key behavior:
- Reads current softfloat rounding mode using `fpgetround()`.
- Converts it to fenv rounding constants with `__FER`.
