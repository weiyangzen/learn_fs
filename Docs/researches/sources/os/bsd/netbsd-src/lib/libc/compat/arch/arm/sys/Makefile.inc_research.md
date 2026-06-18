# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/Makefile.inc

## Scope

ARM compatibility syscall wrapper build fragment.

## Behavior

- Adds wrappers for old vfork, SysV IPC controls, signal operations, signal trampoline, and quota control.

## Dependencies And Invariants

- Depends on ARM `SYS.h` and ARM EABI/APCS syscall conventions.
