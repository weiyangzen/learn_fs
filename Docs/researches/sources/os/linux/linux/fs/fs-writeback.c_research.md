# File Research: sources/os/linux/linux/fs/fs-writeback.c

Read status: complete, 3082 lines.

Purpose: core Linux writeback engine for dirty inode/page writeout, flusher work scheduling, cgroup writeback ownership, dirtytime expiration, and sync helpers.

Key flow:
- Defines `struct wb_writeback_work`, writeback work queuing, completion waiting, and per-`bdi_writeback` wakeup/delayed wakeup helpers.
- Maintains dirty IO list state across `b_dirty`, `b_io`, `b_more_io`, and `b_dirty_time`, including bandwidth accounting via `WB_has_dirty_io`.
- With `CONFIG_CGROUP_WRITEBACK`, attaches inodes to cgroup-specific writeback contexts, detects foreign dirtier ownership using history plus Boyer-Moore majority voting, and asynchronously switches inode writeback ownership through `inode_switch_wbs_work_fn()`.
- Splits writeback work across per-bdi writeback contexts proportionally to write bandwidth.
- `queue_io()` moves expired dirty and dirtytime inodes into dispatch queues.
- `__writeback_single_inode()` runs `do_writepages()`, optionally waits for data, handles lazytime expiration, clears/reinstates dirty flags with memory barriers, writes inode metadata, and tracks netfs writeback pinning.
- `writeback_sb_inodes()` and `__writeback_inodes_wb()` batch writeback by superblock and inode list, balancing progress, lock dropping, I_SYNC handling, and requeue decisions.
- `wb_writeback()`, `wb_do_writeback()`, and `wb_workfn()` are the flusher work loop, processing explicit work, start-all, dontcache, periodic old-data, and background threshold writeback.
- Public wakeup helpers start flusher work for one bdi or all bdis.
- Dirtytime infrastructure periodically wakes writeback for `I_DIRTY_TIME` inodes and exposes `vm.dirtytime_expire_seconds`.
- `__mark_inode_dirty()` notifies filesystems of dirty inode state, handles dirtytime promotion, attaches writeback context, and queues inodes on the correct dirty list.
- Sync helpers include `writeback_inodes_sb_nr()`, `writeback_inodes_sb()`, `try_to_writeback_inodes_sb()`, `sync_inodes_sb()`, `write_inode_now()`, and `sync_inode_metadata()`.

Important dependencies: backing-dev writeback infrastructure, page cache tags, memcg/cgroup writeback, block plug flushing, superblock locks, inode state bits, tracepoints, sysctl.

Concurrency/security notes:
- Lock ordering spans `wb->list_lock`, `inode->i_lock`, `mapping->i_pages`, `sb->s_umount`, `s_inode_wblist_lock`, and `wb_switch_rwsem`.
- Memory barriers pair dirty marking with dirty clearing so lockless state checks do not lose dirty events.
- Sync paths guard against inode writeback context switching and wait on in-flight page writeback lists.
- Cgroup inode switching pins superblocks during switch work to avoid umount races.
