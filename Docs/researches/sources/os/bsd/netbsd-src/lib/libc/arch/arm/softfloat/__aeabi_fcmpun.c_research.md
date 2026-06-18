# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpun.c

This EABI helper reports unordered single-precision comparisons by checking whether either operand is unequal to itself through SoftFloat equality. Both operands are tested to handle signaling NaNs.
