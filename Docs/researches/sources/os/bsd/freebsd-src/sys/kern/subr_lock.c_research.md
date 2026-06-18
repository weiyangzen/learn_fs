# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_lock.c

## Purpose
Provides common lock-object initialization/destruction, adaptive delay configuration, debugger display support, and optional lock profiling infrastructure. It is shared by FreeBSD mutex, sx, rw, rm, and lockmgr classes.

## Main Interfaces
- `lock_init()`, `lock_destroy()`: initialize and tear down `struct lock_object`, including lock class index encoding, WITNESS, and lock logging hooks.
- `lock_delay()`, `lock_delay_default_init()`: exponential spin-delay support for lock acquisition loops.
- DDB `show lock`: displays lock class/name and delegates class-specific display.
- Under `LOCK_PROFILING`: profiling hooks for lock acquisition, release, thread exit, sysctl output, reset, and enable.

## Implementation Notes
`lock_classes[]` maps lock class pointers to compact class indices stored in `lo_flags`. `CTASSERT(LOCK_CLASS_MAX == 15)` ensures the fixed layout matches expectations.

The profiling subsystem keeps per-CPU caches of profiling records and per-thread lists of currently held locks. It separates spin and non-spin objects so profiling code can tolerate spinlock acquisition while already profiling a non-spinlock path. Reset disables profiling, publishes the disabled state with fences, waits for critical sections to quiesce, clears per-CPU objects, reinitializes free lists, then restores prior enable state.

Profiling records aggregate hold time, wait time, max values, acquire counts, and contested acquisition counts by `(file, line, lock name)`.

## Dependencies
Uses WITNESS, lock logging, DDB, sysctl, per-CPU storage, scheduler/quiescence primitives, `sbuf`, and optional lock profiling compile-time configuration.

## Research Notes
This file is kernel infrastructure rather than filesystem code, but filesystem and VFS locks depend on these lock-object lifecycle and debugging facilities. The profiling path is careful about CPU migration, reset races, critical sections, and thread exit cleanup.
