# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/or1k/pthread_md.h

## Purpose
OpenRISC/or1k machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` with inline assembly currently loading zero via `l.ori`.
- Defines ucontext stack pointer access as general register index `1`.

## Dependencies
- or1k mcontext layout.
