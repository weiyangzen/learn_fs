# File Research: sources/os/bsd/freebsd-src/sys/sys/exec.h

## Purpose
Defines process startup argument metadata, executable image switch registration, and kernel helpers for exec image activators.

## Main Interfaces
- `struct ps_strings`: argv/env pointer and count block historically placed at top of user stack.
- `struct execsw`: executable image activator function pointer and name.
- Kernel macros:
  - `PS_STRINGS`
  - `PROC_PS_STRINGS`
  - `PROC_SIGCODE`
  - `PROC_HAS_SHP`
- Kernel APIs:
  - `exec_map_first_page`
  - `exec_unmap_first_page`
  - `exec_register`
  - `exec_unregister`
- `EXEC_SET`: module registration macro for executable image handlers.

## Dependencies And Integration
Includes machine-specific `machine/exec.h`; kernel path includes module support. Image activators plug into the exec subsystem through `execsw`.

## Risk Notes
`ps_strings` is user ABI and still used as a fallback by process argument sysctls. `EXEC_SET` depends on module init ordering at `SI_SUB_EXEC`.
