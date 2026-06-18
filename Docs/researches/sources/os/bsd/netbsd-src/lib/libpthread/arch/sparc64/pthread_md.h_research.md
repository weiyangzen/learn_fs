# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/sparc64/pthread_md.h

## Purpose
SPARC64 machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `%sp`.
- Defines ucontext stack pointer access via `_REG_O6`.

## Dependencies
- SPARC64 mcontext register layout.
