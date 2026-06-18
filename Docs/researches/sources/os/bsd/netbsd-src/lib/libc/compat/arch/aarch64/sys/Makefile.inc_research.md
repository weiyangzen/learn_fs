# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/Makefile.inc

## Scope

AArch64 compatibility syscall wrapper build fragment.

## Behavior

- Adds compatibility assembly sources for old `vfork`, SysV IPC controls, signal action/mask/pending/return/suspend, and quota control.
- Leaves `compat___sigtramp1.S` commented out.

## Dependencies And Invariants

- Source list must match kernel compatibility syscall names and AArch64 `SYS.h` wrapper macros.
