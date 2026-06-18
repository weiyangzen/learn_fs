# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_pool.h

Read status: complete, 195 lines.

Purpose: DSL pool state and pool-wide sync/dirty-space/configuration APIs.

Key structures and APIs:
- Dirty-data tunables are declared as externs.
- `zfs_blkstat_t` and `zfs_all_blkstats_t` store block statistics by level and object type.
- `dsl_pool_t` stores SPA, meta objset, root/MOS/free/leak dirs, origin snapshot, taskqs, meta root block pointer, temporary userrefs object, free/bptree/empty/obsolete block pointer objects, scan state, dirty-space counters, MOS deltas, delayed transaction wakeup time, TXG state/lists, sync task queues, config rrwlock, and block stats.
- APIs cover init/open/close/create/sync/sync_done, sync-context detection, adjusted/unreserved space, dirty/undirty space, block free/free_sync, origin creation, clone upgrades, MOS/checkpoint space accounting, config lock enter/exit/held checks, dirty-delay decision, taskq access, user hold/release, tmp userref cleanup, special dir open, pool hold/release, and obsolete bpobj lifecycle.

Important implementation constraints:
- `dp_config_rwlock` protects administrative changes and is only write-held in syncing context.
- Dirty space is tracked per-TXG plus total.
- Sync tasks, early sync tasks, dirty datasets, dirty ZILs, and dirty dirs are TXG lists.

Dependencies: SPA, TXG internals, ZFS context, ZIO, dnode, DDT, ARC, bpobj, bptree, rrwlock, DSL synctask, MMP.

Research notes:
- This is the central coordination object for DSL syncing, dirty throttling, config locking, and pool-level deferred frees.
