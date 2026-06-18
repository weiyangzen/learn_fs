# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_kthread.c

## Purpose

`kern_kthread.c` provides small wrappers for creating, starting, exiting, and voluntarily suspending DragonFlyBSD lightweight kernel threads.

## Main Responsibilities

- Allocates unscheduled or scheduled LWKT kernel threads with `_kthread_create()`.
- Exposes `kthread_alloc()`, `kthread_create()`, and `kthread_create_cpu()`.
- Installs the target function through `cpu_set_thread_handler()` with `kthread_exit()` as the return path.
- Sets `td_comm` formatting for diagnostics and `ps`-visible names.
- Holds `proc0` credentials for created kernel threads.
- Starts SYSINIT-described kernel daemons with `kproc_start()`.
- Implements cooperative kernel-thread suspend and resume helpers.

## Behavior

`_kthread_create()` allocates a thread with `lwkt_alloc_thread()`, optionally pins it to a CPU, sets its handler and argument, formats its command name, inherits a held reference to `proc0.p_ucred`, and optionally schedules it immediately. `kproc_start()` creates the thread named by `struct kproc_desc`, raises it to `TDPRI_KERN_DAEMON`, and panics if creation fails.

## Suspension Model

`suspend_kproc()` only accepts kernel threads with no `td_proc`. It sets `TDF_MP_STOPREQ`, wakes the target, and waits until the target cooperatively clears the request. `kproc_suspend_loop()` is called by participating kernel threads in their main loop; it clears `STOPREQ`, sleeps until `TDF_MP_WAKEREQ`, then wakes the controller. A global `kpsus_token` serializes the protocol.
