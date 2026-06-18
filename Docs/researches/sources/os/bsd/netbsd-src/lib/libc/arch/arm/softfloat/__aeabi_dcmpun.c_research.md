# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpun.c

This EABI helper reports unordered double comparisons by testing each operand against itself with `float64_eq`. It performs both checks so signaling NaNs in either operand are observed.
