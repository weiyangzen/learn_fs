# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmplt.c

This helper implements `__aeabi_dcmplt(float64, float64)` as `float64_lt(a, b)`. It is direct compiler support for double less-than comparisons under ARM softfloat.

The file is simple but ABI-facing: symbol spelling and SoftFloat type layout must remain stable.
