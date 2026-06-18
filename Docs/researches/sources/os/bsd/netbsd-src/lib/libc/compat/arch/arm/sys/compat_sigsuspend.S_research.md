# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigsuspend.S

## Scope

ARM compatibility implementation of old `sigsuspend`.

## Behavior

- Defines explicit `ENTRY(sigsuspend)`.
- Dereferences the old signal mask pointer and calls `compat_13_sigsuspend13`.

## Dependencies And Invariants

- Must pass the integer signal mask expected by the compatibility syscall.
