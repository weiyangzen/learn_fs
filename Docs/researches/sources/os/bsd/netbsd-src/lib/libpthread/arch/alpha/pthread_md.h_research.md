# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/alpha/pthread_md.h

## Purpose
Alpha machine-dependent pthread helpers.

## Main Responsibilities
- Enables `PTHREAD__ASM_RASOPS`.
- Defines `pthread__sp()` from register `$30`.
- Defines ucontext stack pointer access via `_REG_SP`.
- Initializes processor status register to Alpha user value `0x0008`.

## Dependencies
- Alpha mcontext register layout.
