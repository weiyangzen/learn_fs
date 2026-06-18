# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat___sigreturn14.S

## Scope

HPPA compatibility wrapper for `__sigreturn14`.

## Behavior

- Defines `PSEUDO(__sigreturn14,compat_16___sigreturn14)`.

## Dependencies And Invariants

- Preserves signal-return ABI and register state assumptions.
