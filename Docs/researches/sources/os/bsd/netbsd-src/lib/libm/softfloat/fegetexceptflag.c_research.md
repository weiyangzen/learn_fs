# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetexceptflag.c

Implements `fegetexceptflag`.

Key behavior:
- Reads softfloat sticky flags.
- Converts them to fenv exception bits with `__FEE`.
- Masks with the caller-requested `excepts` and stores into `*flagp`.
- Always returns 0.
