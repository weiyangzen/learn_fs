# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/unordsf2.S

This m68k hard-float assembly file defines `__unorddf2`, a libgcc-style unordered comparison helper for double-precision values. It loads two stack-passed doubles into the 68881-compatible FPU, performs `fcmpd`, and returns `0` when the comparison branches on unordered/ordered condition label `Lbor`, otherwise `1`.

Its integration point is compiler-emitted floating-point comparison support in libc/libgcc compatibility code. The key risk is ABI exactness: stack offsets, FPU condition-code interpretation, and the mismatch between the filename’s `sf` spelling and the exported `__unorddf2` symbol are all intentional historical port details.
