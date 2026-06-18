# File Research: sources/os/linux/linux-stable/fs/ocfs2/quota_global.c

Purpose: implements OCFS2 operations over the cluster-wide global quota files, including qtree serialization, physical quota block I/O, global quota info updates, periodic local-to-global sync, and Linux quota operation hooks.

Read coverage: complete file read, 1051 lines.

Key responsibilities:
- Converts OCFS2 global on-disk dquot records to/from generic `struct dquot` state with `ocfs2_global_disk2memdqb()` and `ocfs2_global_mem2diskdqb()`.
- Supplies `ocfs2_global_ops` for qtree quota format operations.
- Validates quota metadata ECC trailers and reads quota blocks by physical block number.
- Implements `ocfs2_quota_read()` and `ocfs2_quota_write()` bypassing page cache, using extent maps and direct buffer-head I/O.
- Coordinates global quota file locking through `ocfs2_lock_global_qf()` / `ocfs2_unlock_global_qf()`.

Major logic:
- `ocfs2_global_read_info()` opens the relevant global system quota inode, initializes `ocfs2_mem_dqinfo`, reads qtree header state, initializes qinfo lock resources, and schedules delayed quota sync work.
- `__ocfs2_global_write_info()` persists grace periods, sync interval, qtree block counts, free block, and free entry state.
- `__ocfs2_sync_dquot()` merges local dquot deltas with the global record, preserves admin-set fields, adjusts grace timers, updates origin counters, changes use count on freeing, writes the qtree record, and may release unused global records.
- `qsync_work_fn()` periodically scans active dquots, avoiding `s_umount` deadlock with `down_read_trylock()`.
- `ocfs2_acquire_dquot()` reads or creates a global qtree entry, increments global use count, preallocates space outside a transaction when needed, then creates the corresponding local quota entry.
- `ocfs2_release_dquot()` drops global and local references, with special delayed handling when called from the downconvert thread.

Important entry points:
- Global file/info: `ocfs2_global_read_info()`, `ocfs2_global_write_info()`, `ocfs2_lock_global_qf()`, `ocfs2_unlock_global_qf()`.
- Quota I/O: `ocfs2_quota_read()`, `ocfs2_quota_write()`, `ocfs2_read_quota_phys_block()`.
- Dquot lifecycle: `ocfs2_acquire_dquot()`, `ocfs2_release_dquot()`, `ocfs2_mark_dquot_dirty()`, `ocfs2_get_next_id()`.
- Exported VFS quota ops are collected in `ocfs2_quota_operations`.

Concurrency and dependencies:
- The file documents strict lock ordering among transactions, `dqio_sem`, dquot locks, global quota inode locks, qinfo locks, and local quota inode locks.
- Global quota modification requires global quota inode cluster lock, inode mutex, `ip_alloc_sem`, and qinfo lock.
- Uses OCFS2 journaling, extent maps, inode locking, qinfo DLM locks, local quota helpers, qtree helpers, delayed work, and dquot core APIs.
- Uses `memalloc_nofs_save()` around quota write sections that must not recurse into filesystem allocation.

Risks and edge cases:
- Lock ordering is the dominant correctness risk; violating the documented order can deadlock clustered quota sync or recovery.
- `ocfs2_quota_write()` requires an active transaction and enough credits; it explicitly rejects writes without `journal_current_handle()`.
- New global quota entries may need file extension before transaction start because allocator locking ranks above transaction start.
- Last-reference dquot release cannot safely take quota locks from the downconvert thread, so it queues delayed reference dropping.
- Global and local quota records must remain consistent across acquire, release, periodic sync, and crashed-node recovery.
