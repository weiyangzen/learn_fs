# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmplt.c

This helper implements `__aeabi_fcmplt(float32, float32)` as `float32_lt(a, b)`. It supports compiler-generated ARM softfloat single less-than comparisons.

The main risk is ABI symbol compatibility, not local algorithm complexity.
