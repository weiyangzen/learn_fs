# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fedisableexcept.c

Implements `fedisableexcept`.

Key behavior:
- Reads the current exception enable mask with `fpgetmask()`.
- Clears requested exception-enable bits after translating with `__FPE`.
- Returns the previous enabled exception set translated back with `__FEE`.
