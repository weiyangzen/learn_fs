# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpsetmask.c

This routine reads the old FPCR, replaces only `FPCR_EXCP2` with the requested exception mask, writes the new FPCR, and returns the old mask.
