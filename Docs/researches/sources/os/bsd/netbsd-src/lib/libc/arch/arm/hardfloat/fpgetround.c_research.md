# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpgetround.c

This VFP fenv routine reads `fpscr` and returns the current rounding-mode field using `__SHIFTOUT`. Compile-time assertions verify that VFP rounding encodings match NetBSD `FP_RN`, `FP_RP`, `FP_RM`, and `FP_RZ`.
