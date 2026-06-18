# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/powerpc/pthread_md.h

## Purpose
PowerPC machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from register `r1`.
- Defines ucontext stack pointer access as general register index `1`.
- Initializes MSR to user value `0xd032`.

## Dependencies
- PowerPC mcontext register layout.
