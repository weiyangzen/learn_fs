# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_umtx.c

## Purpose
Implements FreeBSD's `umtx` userland synchronization syscall backend: wait/wake primitives, POSIX mutexes, priority-inheritance and priority-protect mutexes, condition variables, rwlocks, semaphores, robust mutex cleanup, shared umtx backing objects, compatibility ABIs, and syscall dispatch for `_umtx_op`.

## Key Interfaces
- Queue/key primitives: `umtx_key_get()`, `umtx_key_release()`, `umtxq_insert[_queue]()`, `umtxq_remove[_queue]()`, `umtxq_sleep()`, `umtxq_signal_mask()`, `umtxq_requeue()`, and `kern_umtx_wake()`.
- Mutex paths: `do_lock_normal()`, `do_unlock_normal()`, `do_lock_pi()`, `do_unlock_pi()`, `do_lock_pp()`, `do_unlock_pp()`, `do_lock_umutex()`, `do_unlock_umutex()`, `do_wake_umutex()`, `do_wake2_umutex()`, and `do_set_ceiling()`.
- PI support: `umtx_pi_alloc()`, `umtx_pi_ref()`, `umtx_pi_unref()`, `umtx_pi_lookup()`, `umtx_pi_claim()`, `umtx_pi_drop()`, `umtx_pi_adjust()`, and `umtxq_sleep_pi()`.
- Higher-level objects: `do_cv_wait()`, `do_cv_signal()`, `do_cv_broadcast()`, `do_rw_rdlock()`, `do_rw_wrlock()`, `do_rw_unlock()`, `do_sem2_wait()`, `do_sem2_wake()`, plus older semaphore/simple umtx compatibility paths when enabled.
- Syscall dispatch: `sys__umtx_op()`, `kern__umtx_op()`, `freebsd32__umtx_op()`, and the `op_table[]` handlers for each `UMTX_OP_*`.
- Lifecycle hooks: `umtx_thread_init()`, `umtx_thread_fini()`, `umtx_thread_alloc()`, `umtx_exec()`, and `umtx_thread_exit()`.
- Shared-object API: `UMTX_OP_SHM` via `umtx_shm()` creates, looks up, destroys, or checks persistent shared-memory objects backing process-shared umtxes.

## State And Locking
Waiters are represented by per-thread `struct umtx_q` objects and are indexed by `struct umtx_key` values derived from either private vmspace/address pairs or shared VM object/offset pairs. Two sets of `umtxq_chains` hold hash buckets, queue heads, spare queue heads, PI state lists, and busy/waiter counters under per-chain mutexes. The global `umtx_lock` protects PI ownership, inherited-priority state, and PI blocked/owned lists. PI objects are allocated from `umtx_pi_zone`; shared umtx registry entries are allocated from `umtx_shm_reg_zone` and protected by `umtx_shm_lock`. Per-thread robust-list pointers and inherited-priority fields live on the thread's `td_umtxq` and thread fields.

## Control Flow
Wait operations derive a key, enqueue the current thread, verify the user-space word still matches the expected value, sleep with optional absolute or relative timeout, then remove the queue entry and release the key. Wake operations derive the same key, signal one or more matching waiters, and release object references. Normal mutex locking first tries user-space owner CAS cases, then marks contention and sleeps; unlocking validates ownership, chooses an unowned/contested/robust terminal value, wakes one waiter, and repairs contention bits as needed. PI mutexes maintain a kernel `umtx_pi` object per key, order blocked waiters by user priority, lend priority through owner chains, detect wait loops, and disown or transfer state on unlock. PP mutexes validate ceiling priority, optionally lend realtime priority, force kernel involvement by keeping the contested state, and restore inherited priorities on unlock or failed waits.

## Robust Lists And Cleanup
`UMTX_OP_ROBUST_LISTS` registers normal and private robust-list offsets plus an inactive pointer offset, with separate native and compat32 layouts. On thread exit or exec, `umtx_thread_cleanup()` disowns PI mutexes, resets lent priority, walks robust lists up to `kern.ipc.umtx_max_robust`, marks owner-dead or not-recoverable values through the normal unlock path, and logs verbose failures when configured.

## Shared Umtx Objects
`UMTX_OP_SHM` maps a process-shared umtx address to a registry entry keyed by the containing VM object and offset. Create allocates a one-page anonymous shm object subject to `RLIMIT_UMTXP`; lookup returns a file descriptor for the registered object; destroy drops the linked registry reference and marks the VM object dead; alive checks report whether the containing VM object was terminated. Registry entries also hang off the source VM object so object termination can asynchronously unlink and free them.

## ABI And Time Handling
The syscall layer uses `struct umtx_copyops` to abstract native, compat32, i386, and x32 timespec/_umtx_time/robust-list formats. Timeouts can be relative or absolute, use multiple clock IDs, enforce a per-process minimum timeout, align fast clocks to tick or second boundaries, and convert restart behavior so timed operations generally return `EINTR` rather than being transparently restarted.

## Integration Notes
This subsystem sits at the boundary between user memory, VM object identity, scheduler priority lending, MAC/file descriptor policy for shared memory, resource limits, taskqueue deferred freeing, thread suspension checks, and FreeBSD32 compatibility. It uses user-access primitives (`fueword*`, `casueword*`, `suword*`, `copyin/out`) throughout because user memory can fault or change concurrently.

## Risks
The implementation is highly race-sensitive. Correctness depends on the chain `busy` protocol when user memory is inspected or modified outside the chain lock, exact removal from shared versus exclusive queues, preserving VM object references for shared keys, and balancing PI refcounts. Priority propagation must avoid cycles and avoid granting unbounded timeshare boosts. Robust-list cleanup intentionally tolerates inconsistent user memory but can leave user-visible owner-dead/not-recoverable states. Compatibility copy sizes and remaining-time copyout paths are easy to regress because several 32-bit time layouts coexist.
