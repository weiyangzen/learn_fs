# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/Makefile.inc

This ARM libc make fragment adds non-rumprun signal/thread support sources, forces ARM mode for non-earmv7 builds, and includes local headers via `-I.`. For EABI ARM it adds `arm_initfini.c`; for softfloat it includes `softfloat/Makefile.inc` with optional 32-bit helpers, and for hardfloat it builds VFP-backed fenv and `fabs` sources with `-mfpu=vfp`.
