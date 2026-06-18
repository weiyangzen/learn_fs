# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpgt.c

This EABI helper implements double greater-than as `!float64_le(a,b)` with both operands checked against themselves to reject unordered NaN comparisons.
