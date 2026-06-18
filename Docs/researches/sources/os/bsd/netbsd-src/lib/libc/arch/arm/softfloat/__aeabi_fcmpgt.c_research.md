# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpgt.c

This EABI helper implements single greater-than as not-less-or-equal plus explicit orderedness checks using `float32_eq(x, x)`.
