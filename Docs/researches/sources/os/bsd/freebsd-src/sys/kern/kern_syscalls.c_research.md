# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_syscalls.c

## Purpose

Implements dynamic syscall table registration and deregistration support for loadable kernel modules and syscall helper arrays, including concurrency protection for in-flight dynamic syscall execution.

## Main Responsibilities

- Provides placeholder syscall handlers:
  - `lkmnosys()`
  - `lkmressys()`
- Defines `nosys_sysent`, a capability-enabled `nosys` sysent used when dynamic syscall slots are absent or draining.
- Tracks active dynamic syscall users through `sy_thrcnt`.
- Implements dynamic syscall entry/exit accounting:
  - `syscall_thread_enter()`
  - `syscall_thread_exit()`
  - internal `syscall_thread_drain()`
- Registers and deregisters individual syscalls:
  - `kern_syscall_register()`
  - `kern_syscall_deregister()`
- Handles module lifecycle integration:
  - `syscall_module_handler()`
  - `kern_syscall_module_handler()`
- Registers and unregisters arrays of syscall helper records:
  - `syscall_helper_register()`
  - `kern_syscall_helper_register()`
  - `syscall_helper_unregister()`
  - `kern_syscall_helper_unregister()`

## Important Control Flow

- `kern_syscall_register()` either finds a free `lkmnosys` slot when `NO_SYSCALL` is requested or validates a specified slot. It rejects occupied non-placeholder slots, installs the new `sysent`, and publishes `sy_thrcnt` with release ordering.
- `syscall_thread_enter()` increments `sy_thrcnt` for non-static dynamic syscalls. If the syscall is draining or absent, it redirects the caller to `nosys_sysent`.
- `syscall_thread_exit()` decrements the active thread count.
- `syscall_thread_drain()` marks a dynamic syscall as draining and waits until the active count reaches absent before deregistration completes.
- `kern_syscall_module_handler()` registers on `MOD_LOAD`, stores the assigned syscall number in module-specific data, optionally chains module event handlers, and deregisters on `MOD_UNLOAD`.
- Helper registration rolls back already-registered helper syscalls if a later helper registration fails.

## State, Tunables, and Locking

- Uses atomic operations on `sy_thrcnt` with `SY_THR_STATIC`, `SY_THR_DRAINING`, `SY_THR_ABSENT`, and active-count increments.
- Uses `MOD_XLOCK` only to store module-specific syscall number after registration.
- Registration assumes placeholder slots have protected absent state before replacement.

## Filesystem Relevance

This file is not filesystem-specific, but it is relevant to filesystem-related kernel modules that expose syscalls or helper syscall arrays. It ensures module unload does not remove syscall code while threads are still executing it.

## Cautions

- Static syscalls cannot be drained or dynamically deregistered.
- Slot 0 deregistration is treated as a no-op to simplify unload paths.
- Failed module load marks `data->offset = NULL` so unload will not invoke chained unload or deregistration for a syscall that was never installed.
