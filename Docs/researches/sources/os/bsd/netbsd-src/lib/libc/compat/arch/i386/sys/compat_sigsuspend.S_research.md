# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigsuspend.S

## Scope

i386 compatibility implementation of old `sigsuspend`.

## Behavior

- Defines explicit `ENTRY(sigsuspend)`.
- Dereferences the signal mask pointer into the old integer argument slot.
- Calls `compat_13_sigsuspend13`.

## Dependencies And Invariants

- Stack mutation before `SYSTRAP` is required for the old syscall ABI.
