# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/vax/pthread_md.h

## Purpose
VAX machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `%sp`.
- Defines ucontext stack pointer access via `_REG_SP`.
- Initializes PSL to user value `0x03c00000`.
- Marks atomics as memory-barrier-safe.

## Dependencies
- VAX mcontext register layout.
