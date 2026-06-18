# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/riscv/pthread_md.h

## Purpose
RISC-V machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `sp`.
- Defines ucontext stack pointer access via `_REG_SP`.

## Dependencies
- RISC-V mcontext register layout.
