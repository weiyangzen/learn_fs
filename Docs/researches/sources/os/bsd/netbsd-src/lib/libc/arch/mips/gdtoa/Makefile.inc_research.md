# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/gdtoa/Makefile.inc

This make include adds `strtof.c` for MIPS gdtoa support. On MIPS64 non-o32 builds it also adds `strtold_pQ.c` and `strtopQ.c` to support quad/long-double parsing.

The build logic mirrors the architecture’s long-double availability. It has no runtime logic, but incorrect ABI conditionals would include incompatible conversion code.
