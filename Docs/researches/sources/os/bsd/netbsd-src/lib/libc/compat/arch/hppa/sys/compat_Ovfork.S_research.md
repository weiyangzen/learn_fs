# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_Ovfork.S

## Scope

HPPA compatibility wrapper for `vfork`.

## Behavior

- Defines an HPPA `ENTRY(vfork,0)` and uses syscall wrapper machinery for vfork.
- Includes compatibility warning/reference behavior.

## Dependencies And Invariants

- Must follow HPPA return-value and branch conventions for fork-like syscalls.
