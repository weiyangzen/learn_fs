# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/string/Makefile.inc

This make include selects MIPS string routines. It builds `bcmp.S` and `bzero.S`; for MIPS64 it maps several object targets to generic C sources such as `bcopy.c`, `memcmp.c`, and `memmove.c`, while non-MIPS64 adds `memcmp.S`, `bcopy.S`, and `memmove.S`.

The file encodes ABI/performance tradeoffs between assembly and generic C implementations. Incorrect conditionals could select assembly that is not valid for a given MIPS ABI.
