# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/arm/pthread_md.h

## Purpose
ARM machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` using `sp`.
- Defines SMT wait/wake as WFE/SEV encodings for ARM/Thumb where available, otherwise no-op.
- Defines ucontext stack pointer access via `_REG_SP`.
- Initializes CPSR to user 32-bit mode `0x10`.

## Dependencies
- ARM register layout and compiler mode macros.
