# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpsetround.c

This routine reads the old FPCR, replaces only `FPCR_ROUND` with the requested rounding mode, writes the new FPCR, and returns the old rounding mode.
