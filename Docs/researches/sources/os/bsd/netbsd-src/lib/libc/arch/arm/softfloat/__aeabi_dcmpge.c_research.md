# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpge.c

This EABI helper implements double greater-or-equal as `!float64_lt(a,b)` plus self-equality checks on both operands, so unordered NaN inputs produce false.
