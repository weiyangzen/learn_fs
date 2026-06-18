# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/Makefile.inc

This ARM string make fragment builds selected assembler string routines. It uses naive `memchr`, `strchr`, and `strrchr`, includes `bcopy.S` and `bzero.S`, and conditionally selects optimized or naive implementations based on `ARM_MAX_ARCH` and Thumb capability, with lint stub source tracking for assembly-backed functions.
