# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpgetsticky.S

This VFP fenv routine reads `fpscr`, masks with `VFP_FPSCR_CSUM`, and returns the cumulative floating-point exception flags. It rejects non-VFP builds with a preprocessor error.
