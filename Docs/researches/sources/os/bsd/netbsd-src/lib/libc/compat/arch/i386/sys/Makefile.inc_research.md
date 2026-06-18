# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/Makefile.inc

## Scope

i386 compatibility syscall wrapper build fragment.

## Behavior

- Adds wrappers for old vfork, SysV IPC controls, signal operations, signal trampoline, and quota control.

## Dependencies And Invariants

- Source list must align with i386 old syscall ABI and stack argument layout.
