# File Research: sources/os/linux/linux/fs/gfs2/glock.c

## Scope

Implements the GFS2 glock core: glock lookup/allocation, reference lifetime, holder enqueue/dequeue, local compatibility, DLM state transitions, demotion handling, lock reply completion, glock LRU/shrinker disposal, inode-delete verification work, withdrawal/thaw/unmount cleanup, and debugfs reporting.

## Public And Internal APIs Covered

- Lifetime and lookup: `gfs2_glock_get()`, `gfs2_glock_hold()`, `gfs2_glock_put()`, `gfs2_glock_put_async()`, `gfs2_glock_free()`, `gfs2_glock_free_later()`.
- Holder lifecycle: `__gfs2_holder_init()`, `gfs2_holder_reinit()`, `gfs2_holder_uninit()`, `gfs2_glock_nq()`, `gfs2_glock_wait()`, `gfs2_glock_dq()`, `gfs2_glock_dq_uninit()`.
- Multi-glock acquisition: `gfs2_glock_nq_m()`, `gfs2_glock_dq_m()`, async wait/retry via `gfs2_glock_async_wait()`.
- DLM callbacks: `gfs2_glock_cb()`, `gfs2_glock_complete()`.
- Inode deletion coordination: `gfs2_queue_try_to_evict()`, `gfs2_queue_verify_delete()`, `gfs2_cancel_delete_work()`, `gfs2_flush_delete_work()`.
- Global maintenance: `gfs2_gl_hash_clear()`, `gfs2_withdraw_glocks()`, `gfs2_glock_thaw()`, `gfs2_glock_init()`, `gfs2_glock_exit()`.
- Debugging: `gfs2_dump_glock()`, `gfs2_create_debugfs_file()`, `gfs2_delete_debugfs_file()`, debugfs `glocks`, `glockfd`, `glstats`, `sbstats`.

## Control Flow And Behavior

- Glocks live in a global `rhashtable` keyed by `lm_lockname`; concurrent insertion waits on a hashed waitqueue when a dying glock with the same name is being removed.
- `may_grant()` enforces local compatibility: exclusive is exclusive except node-scope sharing, shared matches shared, deferred matches deferred, and `LM_FLAG_ANY` can accept compatible non-unlocked states.
- `gfs2_glock_nq()` queues holders, rejects impossible try-locks early, traps recursive non-flock locking by the same pid, and runs the queue; synchronous holders wait on `HIF_WAIT`, async holders rely on polling/wait APIs.
- `run_queue()` promotes locally grantable holders, starts DLM conversions through `do_xmote()`, and handles pending demotes only when current holders permit.
- `do_xmote()` invokes glock operation sync/invalidate hooks before demotion, avoids new locking operations after withdrawal, issues DLM `lm_lock()` when available, or completes locally.
- `finish_xmote()` records DLM replies, retries unlock/convert deadlock paths, reports try-lock failures, calls `go_xmote_bh`, promotes waiters, and wakes blocked holders.
- Remote callbacks call `request_demote()`, optionally delay inode demotion using adaptive hold time, and queue glock work.
- LRU/shrinker code demotes or frees idle glocks, sorting disposal by glock number to improve disk access locality.
- Iopen delete work evicts cached inodes or verifies deleted generations using `gfs2_lookup_by_inum()`.
- Unmount sets `SDF_SKIP_DLM_UNLOCK`, flushes work, demotes/clears all glocks, waits for `sd_glock_disposal`, unmounts locking, frees deferred dead glocks, and destroys the workqueue.

## State And Invariants

- `gl_lockref.lock` protects glock state, target, demote state, holder list, reply fields, and object pointer.
- `GLF_LOCK` serializes DLM conversion; `GLF_DEMOTE_IN_PROGRESS` is only valid while `GLF_LOCK` is set.
- `GLF_HAVE_FROZEN_REPLY` defers replies during DLM recovery unless a recovery holder is present.
- Holders must be removed from `gl_holders` before uninit; uninit drops the glock reference and pid reference.
- `GL_NOCACHE` forces demotion to unlocked on release.
- The LRU contains only unreferenced, non-dead glocks that may still have DLM state.
