# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigaction.S

## Scope

i386 compatibility wrapper for old `sigaction`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(sigaction,compat_13_sigaction13)`.

## Dependencies And Invariants

- Routes to NetBSD 1.3 signal action ABI.
