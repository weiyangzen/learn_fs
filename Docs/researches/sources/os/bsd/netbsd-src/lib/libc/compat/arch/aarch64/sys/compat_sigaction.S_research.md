# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigaction.S

## Scope

AArch64 compatibility wrapper for old `sigaction`.

## Behavior

- Emits a warning reference recommending `<signal.h>`.
- Defines `PSEUDO(sigaction,compat_13_sigaction13)`.

## Dependencies And Invariants

- Routes to the NetBSD 1.3 signal action ABI.
