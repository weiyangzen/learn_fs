# File Research: sources/os/linux/linux-stable/fs/gfs2/glock.c

## Scope

This file implements the GFS2 glock core: creation and lookup, holder queueing, local compatibility checks, DLM promote/demote state transitions, asynchronous completion, instantiate hooks, LRU/shrinker reclamation, iopen delete verification, withdrawal handling, unmount cleanup, and debugfs reporting.

## Public And Internal APIs Covered

- Lifetime: `gfs2_glock_get()`, `gfs2_glock_hold()`, `gfs2_glock_put()`, `gfs2_glock_put_async()`, `gfs2_glock_free()`, `gfs2_glock_free_later()`.
- Holder lifecycle: `__gfs2_holder_init()`, `gfs2_holder_reinit()`, `gfs2_holder_uninit()`.
- Acquire/release: `gfs2_glock_nq()`, `gfs2_glock_wait()`, `gfs2_glock_poll()`, `gfs2_glock_dq()`, `gfs2_glock_dq_wait()`, `gfs2_glock_dq_uninit()`, `gfs2_glock_nq_num()`, `gfs2_glock_nq_m()`, `gfs2_glock_dq_m()`.
- Completion/callback: `gfs2_glock_cb()`, `gfs2_glock_complete()`, `gfs2_glock_thaw()`.
- Object and delete tracking: `glock_set_object()`, `glock_clear_object()`, `gfs2_inode_remember_delete()`, `gfs2_inode_already_deleted()`, `gfs2_queue_try_to_evict()`, `gfs2_queue_verify_delete()`, `gfs2_cancel_delete_work()`, `gfs2_flush_delete_work()`.
- Global maintenance: `gfs2_withdraw_glocks()`, `gfs2_gl_hash_clear()`, `gfs2_glock_init()`, `gfs2_glock_exit()`.
- Debugfs: `gfs2_dump_glock()`, `gfs2_create_debugfs_file()`, `gfs2_delete_debugfs_file()`, `gfs2_register_debugfs()`, `gfs2_unregister_debugfs()`.

## Control Flow And Behavior

- Glocks are keyed by `lm_lockname` in a global rhashtable. Lookup uses RCU and a wait queue keyed by the same lockname so callers can wait while a dying glock is removed.
- New glocks are initialized with operation type, optional LVB, optional address_space, lockref, stats, holder list, delayed work, and iopen delete work.
- `may_grant()` encodes local compatibility: exclusive is incompatible except for node-scope exclusive sharing, shared only shares with shared, deferred only shares with deferred, and `LM_FLAG_ANY` can accept compatible non-unlocked current states.
- `gfs2_glock_nq()` queues a holder, rejects recursive acquisitions by the same pid except flock glocks, handles nonblocking fast path, and runs the queue. Synchronous callers wait for `HIF_WAIT` to clear, then instantiate if needed.
- `run_queue()` chooses between demotion and promotion. Demotion waits for holders to drain, sets `GLF_DEMOTE_IN_PROGRESS`, and calls `do_xmote()`. Promotion grants locally compatible holders or starts a DLM conversion to the first waiter’s state.
- `do_xmote()` invokes glops sync/invalidate hooks before DLM conversion. On withdrawal it discards cached state and avoids issuing new DLM operations. Async DLM conversions hold an extra glock reference until completion.
- `finish_xmote()` consumes DLM replies, updates state, handles canceled/try/error results, retries deadlock/unlock cases, invokes `go_xmote_bh`, promotes waiters, and clears `GLF_LOCK`.
- Remote callbacks call `request_demote()`, possibly delaying inode demotion by the adaptive hold time to reduce lock bouncing.
- Async multi-glock acquisition uses `GL_ASYNC`, waits with randomized/exponential timeout, and returns `-ESTALE` to tell callers to release and retry.
- LRU/shrinker paths demote and release unused glocks. Glocks with active locks, references, or log-flush state are preserved.
- Iopen delete work tries to evict local cached inodes on remote iopen contention, then verifies deleted inode generations by looking up unlinked dinodes and rescheduling on `-EAGAIN`.
- Unmount sets `SDF_SKIP_DLM_UNLOCK`, flushes workqueues, demotes/clears glocks, waits for disposal with warnings, unmounts the lock module, frees delayed-dead glocks, and dumps leftovers.
- Debugfs iterators expose glock state, per-glock stats, per-superblock per-cpu stats, and currently open file descriptors holding iopen/flock glocks.

## State And Data Structures

- Global state: `gl_hash_table`, glock wait table, global LRU list/count/lock, shrinker, debugfs root.
- Glock state: `gl_flags`, current/target/demote state, DLM reply, lockref, holders, glops, LVB, object pointer, AIL counters, delayed work, iopen delete fields, rhashtable node, and RCU head.
- Holder state: requested state, flags, owner pid, wait/holder bits, error, and caller return address for diagnostics.
- Superblock state used here: glock and delete workqueues, async wait queue, kill wait, lockstruct ops/recovery flags, dead glocks, and disposal counter.

## Dependencies

- DLM lock operations through `lm_lockops`.
- Glops callbacks from `glops.c` for sync, invalidate, instantiate, held, dump, and remote callback behavior.
- Inode lookup/eviction helpers in `inode.c` and VFS dcache pruning for iopen delete work.
- Linux rhashtable, lockref, RCU, workqueues, shrinker, debugfs, seq_file, pid namespaces, and file table helpers.

## Risks And Invariants

- `gl_lockref.lock` protects holder queues and state bits; many functions temporarily drop and reacquire it around sleeping or callback operations.
- `GLF_LOCK` and `GLF_DEMOTE_IN_PROGRESS` ordering is critical; the code asserts demote-in-progress only occurs while locked.
- Recursive lock detection prevents self-deadlock, but intentionally exempts flock glocks.
- Async DLM completion and workqueue reference accounting must balance exactly; queued work owns a glock reference.
- `go_sync()` / `go_inval()` are intentionally skipped or modified during withdrawal to avoid new shared-device writes.
- Iopen delete verification depends on generation tracking in the LVB to avoid confusing stale inode numbers with live recreated inodes.
