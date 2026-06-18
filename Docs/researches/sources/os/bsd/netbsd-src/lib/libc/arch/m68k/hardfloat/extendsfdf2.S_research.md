# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/extendsfdf2.S

This helper implements `__extendsfdf2`, converting a single-precision input to double by loading it into the FPU and storing a double result for non-SVR4 ABI callers.
