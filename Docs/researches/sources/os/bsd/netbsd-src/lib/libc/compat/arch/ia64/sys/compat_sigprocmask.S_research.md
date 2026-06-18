# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_sigprocmask.S

## Scope

IA64 compatibility wrapper for old `sigprocmask`.

## Behavior

- Defines `PSEUDO(sigprocmask,compat_13_sigprocmask13)`.

## Dependencies And Invariants

- Uses the old NetBSD 1.3 signal-mask compatibility syscall.
