# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/t_lock.h

## Purpose
Aggregates core kernel synchronization headers and declares dispatcher-lock routines/macros.

## Main Interfaces
- Includes, outside assembly:
  - `sys/machlock.h`
  - `sys/param.h`
  - `sys/mutex.h`
  - `sys/rwlock.h`
  - `sys/semaphore.h`
  - `sys/condvar.h`
- Kernel dispatcher lock routines:
  - `disp_lock_enter()`, `disp_lock_exit()`
  - high-priority and no-preempt variants
  - `disp_lock_init()`, `disp_lock_destroy()`
- Dispatcher lock macros:
  - `DISP_LOCK_INIT()`
  - `DISP_LOCK_HELD()`
  - `DISP_LOCK_DESTROY()`
- Static/runtime assertion placeholders:
  - `NO_LOCKS_HELD`
  - `NO_COMPETING_THREADS`

## Dependencies And Relationships
Used by scheduler and synchronization users. `disp_lock_t` is defined in `machlock.h`.

## Research Notes
The file is mostly an include/dispatcher-lock boundary. It preserves compatibility with assembly consumers via `_ASM` guards.
