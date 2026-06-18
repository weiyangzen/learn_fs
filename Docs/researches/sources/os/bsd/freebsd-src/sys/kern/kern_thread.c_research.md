# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_thread.c

Read status: complete file reviewed.

This file implements FreeBSD's core thread lifecycle machinery: thread object allocation, TID allocation and lookup, process-thread linkage, zombie reaping, COW credential/limit handling, thread exit, process single-threading/suspension, and TID hash maintenance.

Global resources include the UMA `thread_zone`, per-memory-domain zombie lists, reap task/callout, `tid_lock` and `tid_bitmap`, TID hash tables with per-bucket rwlocks, `maxthread`, and atomic `nthreads`. Eventhandler lists support thread constructor/destructor/init/fini hooks. Architecture KBI asserts pin selected `struct thread` and `struct proc` offsets on amd64/i386.

Allocation starts with `thread_count_inc`, which opportunistically reaps zombie threads, enforces `kern.maxthread`, allows privileged reserve use near the limit, and rate-limits warnings. `tid_alloc` assigns IDs from a bitmap above `NO_PID`; batch helpers amortize freeing TIDs and decrementing thread counts during reaping.

UMA callbacks initialize and tear down type-stable thread fields: scheduler state, critical nesting, audit/DTrace/umtx state, sleepqueues, turnstiles, allocation domain, and eventhandler callbacks. `threadinit` initializes global locks/tables, reserves thread0/TID0, creates the zone and hash locks, starts the reap callout, and registers the suspend AST.

Exited threads are placed on per-domain lock-free zombie stacks by `thread_zombie`/`thread_stash`. `thread_reap_domain`, `thread_reap`, `thread_reap_all`, callout/task callbacks, and `thread_reap_barrier` drain dead threads, invoke destructors, batch-release TIDs/creds/limits/counts, free kernel stacks, drain sleep callouts, and return objects to UMA.

`thread_alloc`, `thread_recycle`, `thread_free`, and `thread_free_batched` allocate kernel stacks, sanitizer state, MD state, cpusets, lock profiling state, and callouts. COW helpers (`thread_cow_get_proc`, `thread_cow_get`, `thread_cow_free`, `thread_cow_update`, `thread_cow_synced`) manage per-thread credential and limit references against process generation counters.

Process linkage functions `proc_linkup0`, `proc_linkup`, `thread_link`, and `thread_unlink` initialize thread queues, signal queues, process ksi state, per-thread contested/profiling/epoch lists, sleep callouts, and `p_numthreads`.

`thread_exit` is the low-level irreversible exit path. It requires proc and scheduler locks, drops MD resources, unlinks non-last threads, updates exit-thread counts, calls scheduler exit hooks, wakes single-thread waiters when appropriate, notifies PMC/HWT, records runtime/rusage, marks the thread inactive, handles witness exit, and enters `sched_throw`. `thread_wait` cleans the last remaining thread during process reap.

Single-threading and suspension are handled by `thread_single`, `thread_suspend_check`, `thread_check_susp`, `thread_suspend_switch`, `thread_suspend_one`, `thread_unsuspend_one`, `thread_unsuspend`, `thread_run_flash`, and `thread_single_end`. They support exec/exit single-threading, boundary-only suspension, all-process stops, ptrace suspend requests, interruptible sleep aborts, AST scheduling, boundary counters, and wakeups when all other threads have stopped.

TID lookup uses `tdfind_hash` and `tdfind`: lookup first snapshots thread/proc under the TID hash lock, then locks and verifies the proc because thread exit establishes the opposite lock order. `tidhash_add` and `tidhash_remove` maintain hash membership.

Risk areas are TID reuse and lookup verification, zombie reaping synchronization with CPU deadthread handoff, lock ordering across proc locks, scheduler locks, TID hash locks, and sleepqueues, exact `p_suspcount/p_boundary_count` accounting, single-thread exit races, and ensuring COW credentials/limits are released exactly once.
