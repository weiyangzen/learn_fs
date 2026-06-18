# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_lwp.c

## Purpose
Implements NetBSD lightweight process (LWP) lifecycle and core thread management: initialization, creation, start, suspend/continue, wait/reap, exit/free, migration, lookup, locking helpers, user-return handling, LWP references, per-LWP user control pages, private data, and DDB stack ownership reporting.

## Main Interfaces
- `lwpinit`, `lwp0_init`: initialize global LWP pool/list, sysctl `kern.maxlwp`, and bootstrap LWP state.
- `lwp_create`, `lwp_start`, `lwp_startup`: allocate and initialize LWPs, assign LIDs, inherit state, fork MD/VM/scheduler data, and transition new LWPs into runnable/suspended/stopped execution.
- `lwp_exit`, `lwp_free`: orderly LWP teardown, zombie transition, detached-LWP recycling, accounting merge, signal cleanup, LID freeing, and pool return.
- `lwp_suspend`, `lwp_continue`, `lwp_unstop`, `lwp_wait`: implement user-visible suspend/continue/wait semantics and process-level stopped/suspended state recovery.
- `lwp_migrate`: retargets LWPs to another CPU depending on current scheduler state.
- `lwp_find2`, `lwp_find`, `lwp_find_first`, `lwp_alive`: lookup live LWPs while excluding `LSIDL` and `LSZOMB`.
- `lwp_lock`, `lwp_trylock`, `lwp_unlock`, `lwp_unlock_to`, `lwp_setlock`, `lwp_locked`: handle the movable per-LWP lock pointer.
- `lwp_userret`, `lwp_need_userret`: process pending user-return work such as signals, credential refresh, suspend, exit, and lwpctl CPU publication.
- `lwp_ctl_alloc`, `lwp_ctl_free`, `lwp_ctl_exit`, `lwp_pctr`, `lwp_setprivate`, `lwp_thread_cleanup`.

## Internal State And Dependencies
- Global `alllwp` list and `lwp_cache` pool cache store active/reusable `struct lwp` objects.
- Bootstrap `lwp0` and `turnstile0` are statically initialized.
- Integrates with scheduler state (`sched_lwp_fork`, `setrunnable`, `mi_switch`, per-CPU `spc_lwplock`/`spc_mutex`), process locks/counters, pid table LWP IDs, credentials, file descriptors, signals, ptrace events, DTrace probes, PCU state, UVM LWP uareas, futex robust-list cleanup, kcov/kmsan, and optional DDB.
- LWP lookup safety depends on keeping selected fields valid even after pid-table lockless lookup races.

## Control Flow Notes
- New LWPs start in `LSIDL`, receive a LID before becoming visible, are inserted into process lists under `p_lock`, then into `alllwp` under `proc_lock`.
- `lwp_start` chooses `LSSTOP`, `LW_WSUSPEND`, or `setrunnable` based on process stop state and flags.
- `lwp_exit` first avoids last-live-LWP partial exit by delegating to `exit1`, then cleans thread resources, removes global visibility, drains references, marks `LSZOMB`, wakes waiters, and switches away if current.
- `lwp_free` waits for `LP_RUNNING` to clear with acquire/release pairing, resets the LWP to `LSIDL`, updates process accounting/counters, releases LID and remaining resources, or leaves the object ready for recycling.
- `lwp_userret` loops until `LW_USERRET` work is clear, handling preemption, cached credentials, pending signals, suspend/core-dump parking, process exit, and lwpctl updates.

## Locking And Correctness
- The file documents the main LWP state machine and lock ordering: sleepq -> turnstile -> `spc_lwplock` -> `spc_mutex`.
- `l_mutex` can change as state changes; callers must use `lwp_lock`/`lwp_unlock_to`, not direct mutex operations.
- Process counters for idle/zombie/stopped/suspended states require `p_lock`.
- `lwp_drainrefs` blocks LWP final zombie publication until external holders release references.
- `lwp_ctl_alloc` maps shared user/kernel pages and uses a process-local lock/bitmap allocator.

## Risk Areas
- State transitions are highly lock-sensitive; missed `p_lock` or stale `l_mutex` use can corrupt process counters or sleep/run queues.
- Detached LWP recycling deliberately reuses structures and turnstiles; fields outside `l_startzero` must remain valid.
- `lwp_wait` handles simple mutual wait deadlocks but not arbitrary wait cycles.
- `lwp_need_userret` relies on AST/signotify synchronization for remote running LWPs.
- lwpctl VM mappings and vfork borrowing need careful lifetime handling.

## Filesystem Relevance
Indirect. This file is scheduler/thread substrate used by VFS, file descriptor, futex, and raw I/O code; it does not implement filesystem logic itself.
