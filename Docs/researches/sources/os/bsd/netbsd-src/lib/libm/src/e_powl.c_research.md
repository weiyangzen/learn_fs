# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_powl.c

This file is the long-double dispatch layer for `powl(long double, long double)`.

When long double is available, it selects `../ld80/e_powl.c` for 64-bit mantissa long double and `../ld128/e_powl.c` for 113-bit mantissa long double, rejecting unsupported formats. Without long-double support, `powl` falls back to double `pow`.

It weak-aliases `powl` to `_powl` and depends on `namespace.h`, `math.h`, and `<machine/float.h>`.
