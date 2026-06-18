# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/Makefile.inc

## Summary
VAX string routine build fragment.

## Key Details
- Adds `bcmp.S`, `bcopy.S`, `bzero.S`, `ffs.S`, and `memcmp.S`.
- Also adds `memcpy.S`, `memmove.S`, and `memset.S`.

## Notes
The listed assembly routines provide VAX-tuned memory and string primitives.
