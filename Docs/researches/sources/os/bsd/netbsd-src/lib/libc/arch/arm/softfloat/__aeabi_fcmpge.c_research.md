# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpge.c

This EABI helper implements single greater-or-equal as not-less-than plus self-equality checks on both operands, making unordered NaN inputs false.
