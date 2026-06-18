# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/Makefile.inc

## Summary
Top-level VAX libc architecture build fragment.

## Key Details
- Adds `__longjmp14.c` and `__sigtramp3.S`.
- Adds current directory to `CPPFLAGS`.
- Defines `__LIBC12_SOURCE__` for `assym.h` generation.

## Notes
The signal trampoline version is `3` on VAX.
