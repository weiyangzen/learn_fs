# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/x86_64/pthread_md.h

## Purpose
x86_64 machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `%rsp`.
- Defines ucontext stack pointer access via `_REG_URSP`.
- Initializes user context segment registers and flags.
- Defines SMT pause/wait as `rep; nop`.
- Marks atomics as memory-barrier-safe.
- Provides inline pointer compare-and-swap with locked and non-interlocked variants.

## Dependencies
- x86_64 ucontext register layout and inline assembly.
