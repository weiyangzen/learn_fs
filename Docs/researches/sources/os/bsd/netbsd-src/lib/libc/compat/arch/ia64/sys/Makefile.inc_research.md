# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/Makefile.inc

## Scope

IA64 compatibility syscall wrapper build fragment.

## Behavior

- Adds `compat_Ovfork.S`, `compat___semctl.S`, `compat_sigprocmask.S`, `compat_sigsuspend.S`, and `compat_quotactl.S`.

## Dependencies And Invariants

- Does not list the full signal/sysv-ipc compatibility set used by several other architectures.
