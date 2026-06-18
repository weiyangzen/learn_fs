# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_sigsuspend.S

## Scope

IA64 compatibility wrapper for old `sigsuspend`.

## Behavior

- Defines `PSEUDO(sigsuspend,compat_13_sigsuspend13)`.

## Dependencies And Invariants

- Routes to old signal-mask suspend ABI.
