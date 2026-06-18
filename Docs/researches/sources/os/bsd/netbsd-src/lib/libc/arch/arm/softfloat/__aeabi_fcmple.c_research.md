# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmple.c

ARM EABI float less-or-equal helper.

Key points:
- Exports `__aeabi_fcmple`.
- Delegates to `float32_le(a, b)`.
