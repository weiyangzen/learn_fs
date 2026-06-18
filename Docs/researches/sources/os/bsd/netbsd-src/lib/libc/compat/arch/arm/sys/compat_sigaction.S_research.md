# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigaction.S

## Scope

ARM compatibility wrapper for old `sigaction`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(sigaction,compat_13_sigaction13)`.

## Dependencies And Invariants

- Uses old NetBSD 1.3 signal action ABI.
