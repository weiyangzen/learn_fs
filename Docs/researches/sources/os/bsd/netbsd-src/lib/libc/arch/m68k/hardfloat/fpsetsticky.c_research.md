# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpsetsticky.c

This routine reads the old FPSR, replaces only accumulated exception bits `FPSR_AEX` with the requested sticky flags, writes the FPSR, and returns the old flags.
