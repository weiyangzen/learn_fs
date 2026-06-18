# File Research: sources/os/linux/linux-stable/fs/afs/callback.c

This file handles AFS callback invalidation for vnodes and whole volumes.

Major responsibilities:
- Invalidates mmap mappings after callback breaks by unmapping file page-cache PTEs in workqueue context.
- Handles server-requested callback state reinitialization by expiring callback promises for all volumes known to a server.
- Breaks individual vnode callbacks, clears permit caches, wakes lock waiters, and queues mmap invalidation when needed.
- Looks up volumes by volume ID under RCU/seqlock protection.
- Handles volume-level callback breaks by expiring server and volume callback promises, incrementing the volume callback break counter, and invalidating mmapped vnodes.
- Dispatches batches of callback-break records grouped by volume.

Callback semantics:
- `__afs_break_callback()` clears `AFS_VNODE_NEW_CONTENT`, clears the callback promise, increments `cb_break` only if a promise was present, updates `cb_v_check`, clears permits, and handles lock/mmap side effects.
- Volume callbacks are represented by FID records with vnode and unique both zero.
- Volume-level breaks set `cb_expires_at` to `AFS_NO_CB_PROMISE` for the matching server entry and the volume.
- `cb_v_break` is incremented with release semantics so directory and vnode validation can notice volume-level invalidations.

Concurrency:
- Individual vnode breaks are protected by `cb_lock` seqlock.
- Server volume lists are walked under `server->cell->vs_lock`.
- Volume rb-tree lookup under RCU uses `read_seqbegin_or_lock()` because lockless rb-tree walks can race with mutations.
- Volume-level callback updates take `cb_v_break_lock`.
