# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmple.c

ARM EABI double less-or-equal helper.

Key points:
- Exports `__aeabi_dcmple`.
- Delegates to `float64_le(a, b)`.
