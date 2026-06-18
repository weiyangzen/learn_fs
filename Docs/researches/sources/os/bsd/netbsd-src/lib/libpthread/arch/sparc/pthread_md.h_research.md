# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/sparc/pthread_md.h

## Purpose
SPARC machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `%sp`.
- Defines ucontext stack pointer access via `_REG_O6`.
- Marks atomics as memory-barrier-safe.

## Dependencies
- SPARC mcontext register layout.
