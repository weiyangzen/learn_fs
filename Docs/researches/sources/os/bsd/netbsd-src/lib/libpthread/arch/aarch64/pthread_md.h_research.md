# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/aarch64/pthread_md.h

## Purpose
AArch64 machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` using inline assembly `mov ..., sp`.
- Defines SMT wait/wake with `wfe` and `sev`.
- Defines ucontext stack pointer access via `_REG_SP`.
- Initializes user context SPSR to zero.

## Dependencies
- AArch64 register names in NetBSD ucontext/mcontext headers.
