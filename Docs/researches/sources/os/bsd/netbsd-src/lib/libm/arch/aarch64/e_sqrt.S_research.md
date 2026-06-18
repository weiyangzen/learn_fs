# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/e_sqrt.S

AArch64 assembly implementation of `__ieee754_sqrt`. It uses hardware `fsqrt d0, d0` and returns the double-precision square root directly.
