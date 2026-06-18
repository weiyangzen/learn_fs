# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/string/Makefile.inc

## Summary
SPARC64 string routine build fragment.

## Key Details
- Adds `ffs.S`, `memcpy.S`, `memset.S`, and `strlen.S`.
- Marks `bcopy.S` and `bzero.S` as not sourced.

## Notes
This selects SPARC64-specific primitives while excluding older aliases.
