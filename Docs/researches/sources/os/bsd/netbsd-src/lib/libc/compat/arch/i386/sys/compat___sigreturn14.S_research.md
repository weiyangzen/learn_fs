# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat___sigreturn14.S

## Scope

i386 compatibility wrapper for `__sigreturn14`.

## Behavior

- Customizes `ENTRY` profiling behavior to preserve register state.
- Defines `PSEUDO(__sigreturn14,compat_16___sigreturn14)`.

## Dependencies And Invariants

- Signal-return path must avoid clobbering restored register context.
