# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_kthread.c

## Purpose
Provides FreeBSD kernel process and kernel thread creation, exit, suspend, resume, and combined process/thread helper routines.

## Key Interfaces
- `kproc_start()` starts SYSINIT-described kernel processes.
- `kproc_create()` creates a kernel process via `fork1()` using `RFMEM | RFFDG | RFPROC | RFSTOPPED`.
- `kproc_exit()` reparents the process to init and exits through `exit1()`.
- `kproc_suspend()`, `kproc_resume()`, and `kproc_suspend_check()` implement voluntary process suspension.
- `kthread_start()` and `kthread_add()` create kernel threads, usually under `proc0` or a provided process.
- `kthread_exit()` tears down a kernel thread and exits the process if it is the last thread.
- `kthread_suspend()`, `kthread_resume()`, and `kthread_suspend_check()` implement voluntary thread suspension.
- `kproc_kthread_add()` creates a process on first call, then adds later threads to it.

## State And Locking
Uses process locks, thread locks, proctree lock, tid hash, cpuset kernel-thread affinity, scheduler primitives, and optional HWPMC/KTR hooks. Suspension uses `p_siglist` for kprocs and `TDF_KTH_SUSP` for kthreads.

## Control Flow
Kernel processes are forked stopped, named, assigned a kernel start handler, moved to kernel cpuset policy, priority-adjusted, then scheduled unless `RFSTOPPED` is requested. Kernel threads are allocated, initialized from an existing thread template, linked into the process, added to tidhash, and scheduled. Exit paths wake waiters before dropping into process/thread teardown.

## Integration Notes
Central utility for internal kernel daemons created by SYSINIT and for subsystems that need background kernel execution contexts.

## Risks
`kthread_add1()` returns `ESRCH` if the target process is exiting after allocating `newtd`; this code path relies on surrounding thread allocation semantics and should be checked carefully if modified. Suspension is cooperative; target main loops must call the corresponding check routines.
