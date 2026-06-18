# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/m68k/pthread_md.h

## Purpose
m68k machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `%sp`.
- Defines ucontext stack pointer access via `_REG_A7`.
- Marks atomics as memory-barrier-safe because m68k is not expected to be SMP.

## Dependencies
- m68k mcontext register layout.
