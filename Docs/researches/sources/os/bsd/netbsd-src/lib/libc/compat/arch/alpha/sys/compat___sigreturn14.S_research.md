# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat___sigreturn14.S

## Scope

Alpha compatibility wrapper for `__sigreturn14`.

## Behavior

- Defines `PSEUDO(__sigreturn14,compat_16___sigreturn14)`.

## Dependencies And Invariants

- Preserves compatibility signal-return entry naming for old binaries.
