# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigsuspend.S

## Scope

AArch64 compatibility wrapper for old `sigsuspend`.

## Behavior

- Emits a warning reference recommending `<signal.h>`.
- Defines `PSEUDO(sigsuspend,compat_13_sigsuspend13)`.

## Dependencies And Invariants

- Uses old signal mask representation through the NetBSD 1.3 compatibility syscall.
