# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigprocmask.S

## Scope

AArch64 compatibility wrapper for old `sigprocmask`.

## Behavior

- Emits a warning reference recommending `<signal.h>`.
- Defines `PSEUDO(sigprocmask,compat_13_sigprocmask13)`.

## Dependencies And Invariants

- Bridges libc `sigprocmask` symbol to old signal-mask syscall ABI.
