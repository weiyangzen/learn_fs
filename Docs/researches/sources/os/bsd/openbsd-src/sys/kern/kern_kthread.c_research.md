# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_kthread.c

## Purpose
Provides kernel thread creation, exit, and deferred creation queue support.

## Main Responsibilities
- Creates kernel threads with `kthread_create()`.
- Exits current kernel thread with `kthread_exit()`.
- Queues deferred thread creation callbacks with `kthread_create_deferred()`.
- Runs deferred callbacks once normal kernel-thread creation is available via `kthread_run_deferred_queue()`.

## Key Behavior
`kthread_create()` calls `fork1()` from `proc0` with `FORK_SHAREVM`, `FORK_SHAREFILES`, `FORK_NOZOMBIE`, and `FORK_SYSTEM`, then sets the process command name.

`kthread_exit()` logs non-zero exits and calls `exit1()`.

Deferred creation stores callbacks in a `SIMPLEQ` until `kthread_create_now` is set.

## Dependencies
Uses `fork1()`, `exit1()`, proc0, malloc/free, and kernel locking.

## Research Notes
Kernel threads are implemented as system processes/threads sharing proc0 resources and normally do not leave waitable zombies.
