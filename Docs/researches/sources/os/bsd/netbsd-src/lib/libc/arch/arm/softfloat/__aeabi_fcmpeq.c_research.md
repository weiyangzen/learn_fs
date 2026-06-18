# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpeq.c

ARM EABI float equality helper.

Key points:
- Exports `__aeabi_fcmpeq(float32, float32)`.
- Returns `float32_eq(a, b)`.
