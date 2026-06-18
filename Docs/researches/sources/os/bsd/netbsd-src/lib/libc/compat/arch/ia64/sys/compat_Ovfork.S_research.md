# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_Ovfork.S

## Scope

IA64 compatibility wrapper for `vfork`.

## Behavior

- Minimal wrapper defining `SYSCALL(vfork)`.

## Dependencies And Invariants

- Uses IA64 `SYS.h` syscall macro conventions.
