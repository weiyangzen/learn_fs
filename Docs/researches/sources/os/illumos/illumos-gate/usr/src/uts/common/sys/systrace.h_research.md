# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/systrace.h

## Purpose
Defines the kernel interface between the syscall table and DTrace systrace provider.

## Main Interfaces
- `systrace_sysent_t`: per-syscall DTrace probe IDs and original syscall function pointer.
- Kernel globals:
  - `systrace_sysent`
  - `systrace_sysent32`
  - `systrace_probe`
- Functions:
  - `systrace_stub()`
  - `dtrace_systrace_syscall()`
  - `dtrace_systrace_syscall32()` under `_SYSCALL32_IMPL`

## Dependencies And Relationships
Includes `sys/dtrace.h`. Interposes on syscall entry/return while preserving the underlying syscall handler pointer.

## Research Notes
This is kernel-only. It provides the syscall instrumentation dispatch bridge rather than the DTrace provider implementation itself.
