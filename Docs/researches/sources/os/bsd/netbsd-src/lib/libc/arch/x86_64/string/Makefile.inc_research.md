# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/string/Makefile.inc

## Summary
x86_64 string routine build fragment.

## Key Details
- Adds assembly implementations for `bcopy`, `ffs`, `memchr`, `memcpy`, `memmove`, `memset`, `strcat`, `strchr`, `strcmp`, `strcpy`, `strlen`, `strncmp`, `strrchr`, and `swab`.
- Marks `bzero.c` as not sourced.

## Notes
This fragment selects a broad set of x86_64 assembly string primitives.
