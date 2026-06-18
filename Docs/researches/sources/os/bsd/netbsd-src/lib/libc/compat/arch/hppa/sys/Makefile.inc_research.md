# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/Makefile.inc

## Scope

HPPA compatibility syscall wrapper build fragment.

## Behavior

- Adds wrappers for old vfork, SysV IPC controls, signal operations, signal trampoline, and quota control.

## Dependencies And Invariants

- Depends on HPPA-specific syscall entry conventions in `SYS.h`.
