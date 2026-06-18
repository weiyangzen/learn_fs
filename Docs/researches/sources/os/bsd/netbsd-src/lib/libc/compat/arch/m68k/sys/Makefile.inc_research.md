# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/Makefile.inc

## Scope

m68k compatibility syscall wrapper build fragment.

## Behavior

- Adds wrappers for old vfork, SysV IPC controls, signal operations, signal trampoline, and quota control.

## Dependencies And Invariants

- Depends on m68k `SYS.h`, trap conventions, and stack-based syscall argument layout.
