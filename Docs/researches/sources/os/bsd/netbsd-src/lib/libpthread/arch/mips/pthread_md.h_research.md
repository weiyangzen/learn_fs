# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/mips/pthread_md.h

## Purpose
MIPS machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `$sp`.
- Defines ucontext stack pointer access via `_REG_SP`.

## Dependencies
- MIPS mcontext register layout.
