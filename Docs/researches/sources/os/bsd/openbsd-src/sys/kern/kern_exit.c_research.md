# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_exit.c

## Purpose
Implements process/thread exit, zombie creation, wait/waitid/wait4, reparenting, ptrace orphan handling, and deferred resource reclamation by the reaper thread.

## Main Responsibilities
- Implements `sys_exit()` and `sys___threxit()`.
- Performs main exit teardown in `exit1()`.
- Schedules post-switch cleanup with `exit2()`.
- Frees proc structures with `proc_free()`.
- Runs the `reaper()` kernel thread to free uareas/vmspace and notify parents.
- Implements wait logic in `dowait6()`, `sys_wait4()`, and `sys_waitid()`.
- Finishes zombie collection in `proc_finish_wait()`.
- Handles ptrace parent restoration with `process_untrace()`.
- Reparents children with `process_reparent()`.
- Fully destroys processes with `process_zap()`.

## Key Exit Flow
`exit1()` marks the thread exiting, coordinates single-threaded process exit, records exit status, detaches the thread from active lists, aggregates usage, exits poll kqueue state, closes fd tables, cancels timers, clears tracing/unveil/pins, tears down VM, removes proc/process from lookup lists, reparents children, accumulates rusage, calls `cpu_exit()`, deactivates pmap, and enters scheduler exit.

`exit2()` runs after the dead thread is no longer executing on its old stack/vmspace; it queues the proc on `deadproc` and wakes `reaper()`.

`reaper()` frees remaining VM resources, marks processes as zombie, fires `knote_processexit()`, posts `SIGCHLD`, wakes waiters, or destroys no-zombie processes directly.

## Wait Semantics
`dowait6()` supports `P_ALL`, `P_PID`, and `P_PGID`; handles exited, trapped, stopped, and continued children; supports `WNOWAIT` and `WNOHANG`; and checks the orphan list for ptrace-related parent handoff cases.

## Concurrency
Exit uses `ps_mtx`, deadproc spin-style mutex, process flags, and no-sleep sections after removing proc from global lookup lists. Resource-heavy VM cleanup is deferred to the reaper.

## Dependencies
Interacts with scheduler, UVM, fd cleanup, kqueue process notes, signals, ptrace, accounting, ktrace, semaphores, pledge/unveil cleanup, process groups, and resource limits.

## Research Notes
The split between `exit1()`, `exit2()`, and `reaper()` is central: immediate exit cannot sleep after a certain point, while final VM/uarea reclamation may block.
