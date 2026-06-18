# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/Makefile.inc

## Scope

Alpha compatibility syscall wrapper build fragment.

## Behavior

- Adds compatibility wrappers for old vfork, SysV IPC controls, signal operations, signal trampoline, and quota control.

## Dependencies And Invariants

- Depends on Alpha assembly syscall conventions and `SYS.h`.
