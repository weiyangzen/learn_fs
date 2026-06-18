# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/sh3/pthread_md.h

## Purpose
SH3 machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `r15`.
- Defines ucontext stack pointer access via `_REG_R15`.
- Initializes status register to zero.
- Marks atomics as memory-barrier-safe because SH3 is not expected to be SMP.

## Dependencies
- SH3 mcontext register layout.
