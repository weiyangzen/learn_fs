# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fetestexcept.c

Implements `fetestexcept`.

Key behavior:
- Reads softfloat sticky exception flags with `fpgetsticky()`.
- Converts to fenv exception bits with `__FEE`.
- Returns only requested bits.
- Includes softfloat headers, including optional `softfloat-for-gcc.h`, but the function itself only uses `ieeefp.h` state access.
