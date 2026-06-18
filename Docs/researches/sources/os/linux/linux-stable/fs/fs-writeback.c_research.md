# File Research: sources/os/linux/linux-stable/fs/fs-writeback.c

This file is the VFS writeback engine for dirty inode and dirty page-cache writeout. It schedules and performs data writeback against backing devices, superblocks, inodes, and cgroup writeback domains; inode metadata writeout is coordinated here but filesystem-specific inode serialization happens through `s_op->write_inode()`.

Major responsibilities:
- Define and queue `wb_writeback_work` items for `struct bdi_writeback`.
- Maintain dirty inode lists: `b_dirty`, `b_io`, `b_more_io`, `b_dirty_time`, and cgroup attached lists.
- Wake and run flusher work for explicit writeback, background thresholds, periodic old-data flushing, dirtytime expiration, and start-all requests.
- Move expired dirty inodes into dispatch queues and group/sort writeback by superblock.
- Write back individual inodes through `do_writepages()`, optional data wait, lazytime handling, dirty flag clearing, and `write_inode()`.
- Requeue inodes after writeback based on remaining dirty pages, skipped pages, dirtytime state, or clean state.
- Implement sync-facing APIs: `writeback_inodes_sb*`, `try_to_writeback_inodes_sb`, `sync_inodes_sb`, `write_inode_now`, and `sync_inode_metadata`.
- Track inodes under writeback on each superblock for `sync(2)` wait semantics.
- Mark inodes dirty through `__mark_inode_dirty()`, including filesystem dirty notifications and dirtytime behavior.
- Support cgroup writeback ownership, writeback domain splitting, foreign-dirtier detection, and asynchronous inode writeback-domain switching.

Important design points:
- Writeback work is per `bdi_writeback`, not only per block device; cgroup writeback can create multiple writeback domains per backing device.
- `wb_io_lists_populated()` and `wb_io_lists_depopulated()` maintain `WB_has_dirty_io` and aggregate BDI bandwidth accounting.
- Dirtytime inodes are deliberately excluded from ordinary dirty-IO wakeups until expiration or sync requires them.
- `queue_io()` batches expired inodes from delaying queues into `b_io`, preserving old-first writeback and optionally sorting by superblock.
- `writeback_sb_inodes()` temporarily drops `wb->list_lock` while doing actual inode I/O, then re-locks and requeues carefully.
- `WB_SYNC_ALL` avoids livelock by tagging and syncing the current dirty set in one large pass.
- `wait_sb_inodes()` waits for pages already under writeback even when the inode is no longer dirty.
- Cgroup writeback uses inode ownership heuristics and Boyer-Moore style majority tracking to switch inodes to the dominant writing memcg over time.
- Inode wb switching is asynchronous, RCU-synchronized, and coordinated with `wb_switch_rwsem` to avoid sync missing moved inodes.

Key invariants:
- `wb->list_lock` protects writeback lists; `inode->i_lock` protects inode dirty/sync state; lock ordering is carefully managed.
- Inodes with `I_FREEING`, `I_WILL_FREE`, or `I_NEW` are not normal flusher targets.
- `I_SYNC` pins an inode during writeback and is cleared through `inode_sync_complete()`, which wakes waiters.
- Dirty flag clearing in `__writeback_single_inode()` pairs memory barriers with `__mark_inode_dirty()` to avoid losing concurrent dirtying.
- `I_DIRTY_TIME` cannot be combined with `I_DIRTY_PAGES` in a single `__mark_inode_dirty()` call.
- Only hashed inodes, plus block-device inodes, are added to dirty lists.
- Sync of a superblock requires `s_umount` to be held and serializes waiters through `s_sync_lock`.
- Cgroup writeback must not switch DAX inodes and must flush in-flight switches during superblock teardown.

External interfaces:
- Exports writeback and sync helpers, dirty marking, cgroup writeback hooks, inode writeback-list helpers, and tracepoints.
- Integrates with backing-dev writeback workers, memory cgroups, pagecache tags, block plugging, superblock operations, and vm sysctl `dirtytime_expire_seconds`.
