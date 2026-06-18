# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/i386/pthread_md.h

## Purpose
i386 machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `%esp`.
- Defines ucontext stack pointer access via `_REG_UESP`.
- Initializes user context flags and segment registers from current CPU state.
- Defines SMT pause/wait as `rep; nop`.
- Marks atomics as memory-barrier-safe.
- Provides inline pointer compare-and-swap with locked and non-interlocked variants.

## Dependencies
- i386 ucontext register layout and inline x86 assembly.
