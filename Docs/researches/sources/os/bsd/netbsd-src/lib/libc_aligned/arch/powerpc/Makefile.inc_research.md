# File Research: sources/os/bsd/netbsd-src/lib/libc_aligned/arch/powerpc/Makefile.inc

## Purpose
Selects aligned-safe string/memory routines for PowerPC `libc_aligned`.

## Build Behavior
Adds common libc string source path and compiles C implementations of `memcmp`, `bcopy`, `memcpy`, and `memmove`, explicitly avoiding assembly versions that use unaligned memory access.

## Dependencies
Depends on `${NETBSDSRCDIR}/common/lib/libc/string`.

## Risks And Notes
This is architecture-specific build selection; correctness depends on the referenced C routines preserving strict alignment assumptions.
