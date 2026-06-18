# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat___sigtramp1.S

## Scope

i386 legacy signal trampoline.

## Behavior

- Provides old signal trampoline code for returning from sigcontext-based signal handlers.
- Arranges stack arguments for compatibility signal return.

## Dependencies And Invariants

- The trampoline’s stack layout must match old i386 signal frame construction.
