# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/string/Makefile.inc

## Summary
Lists SH3 architecture-specific string routines.

## Key Details
- Adds `bcopy.S`, `bzero.S`, `ffs.S`, `memset.S`, `memcpy.S`, and `memmove.S` to libc.
- The local `bcopy.S` and `bzero.S` are wrapper includes around the copy/set implementations.

## Notes
This fragment selects assembly-backed string primitives for SH3.
