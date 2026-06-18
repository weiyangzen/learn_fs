# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpsetsticky.S

This routine sets VFP cumulative exception flags. It masks the requested value with `VFP_FPSCR_CSUM`, merges it into `fpscr`, writes the result, and returns the previous sticky flag set.
