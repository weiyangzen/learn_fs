# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat___sigreturn14.S

## Scope

ARM compatibility wrapper for `__sigreturn14`.

## Behavior

- Defines `PSEUDO(__sigreturn14,compat_16___sigreturn14)`.

## Dependencies And Invariants

- Signal return entry must preserve user register state.
