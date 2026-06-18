# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/semctl.c

## Purpose
Adapts the variadic `semctl` API to the kernel's pointer-based `____semctl50` ABI.

## Key Elements
For commands requiring a fourth argument, extracts `union __semun` from `va_arg` and passes `&semun` to `____semctl50`.

## Dependencies
Uses SysV IPC semaphore headers, `<stdarg.h>`, and internal `____semctl50`.

## Behavior/Risks
Commands not listed leave the local union uninitialized but still pass its address, relying on the kernel ignoring it. The lint path uses `memcpy` to placate lint around `va_list`.
