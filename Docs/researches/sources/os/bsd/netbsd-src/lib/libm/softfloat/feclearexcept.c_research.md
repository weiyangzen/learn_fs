# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/feclearexcept.c

Implements `feclearexcept` for the softfloat fenv layer.

Key behavior:
- Converts C fenv exception bits with `__FPE`.
- Clears those bits from the softfloat sticky flags using `fpgetsticky()` and `fpsetsticky()`.
- Always returns 0.
