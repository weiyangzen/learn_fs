# File Research: sources/os/linux/linux/fs/ocfs2/quota_global.c

`quota_global.c` implements OCFS2 operations over the cluster-wide global quota files. It bridges Linux generic quota callbacks with OCFS2’s qtree format, cluster inode locks, journaling, and per-node local quota files.

Main responsibilities:
- Defines qtree format operations for global dquots:
  - `ocfs2_global_disk2memdqb()` imports global quota records while preserving admin-set in-memory fields.
  - `ocfs2_global_mem2diskdqb()` serializes quota limits, usage, grace times, and OCFS2 use counts.
  - `ocfs2_global_is_id()` validates qtree entries against a dquot id.
- Validates and reads quota metadata blocks through `ocfs2_validate_quota_block()` and `ocfs2_read_quota_phys_block()`, including ECC validation.
- Implements direct quota file I/O through `ocfs2_quota_read()` and `ocfs2_quota_write()`, deliberately bypassing page cache because quota paths already rely on quota/cluster locks.
- Provides `ocfs2_lock_global_qf()` / `ocfs2_unlock_global_qf()` to lock the global quota inode, keep a shared global-info buffer head, and take `ip_alloc_sem` in read or write mode.
- Reads and writes global quota info headers with `ocfs2_global_read_info()`, `__ocfs2_global_write_info()`, and `ocfs2_global_write_info()`.
- Synchronizes local dquot deltas into the global qtree in `__ocfs2_sync_dquot()`, preserving grace-time semantics and clearing `DQ_LASTSET` fields after successful reconciliation.
- Periodically syncs active dquots using delayed work:
  - `qsync_work_fn()` scans active dquots without deadlocking unmount by using `down_read_trylock(&sb->s_umount)`.
  - `ocfs2_sync_dquot_helper()` locks the global quota file, starts a journal transaction, syncs the global dquot, and writes the local dquot.
- Implements generic `dquot_operations`:
  - `ocfs2_acquire_dquot()` reads or creates a global qtree entry, increments the OCFS2 use count, extends the global quota file before transaction start when needed, then creates a local quota entry.
  - `ocfs2_release_dquot()` decrements the global use count, releases local quota state, and defers work when called from the downconvert thread to avoid cluster-lock deadlocks.
  - `ocfs2_mark_dquot_dirty()` writes local changes or immediately syncs admin-set fields to the global file when safe.
  - `ocfs2_get_next_id()` enumerates ids from the global qtree.
  - `ocfs2_alloc_dquot()` / `ocfs2_destroy_dquot()` use the OCFS2 dquot slab cache.

Key invariants:
- Global quota file modification requires the global quota inode cluster lock, inode `i_rwsem`, `ip_alloc_sem`, and quota info lock.
- Quota writes require an existing journal transaction; missing transactions are treated as I/O errors.
- Allocation for new global quota file space is done before starting the transaction to preserve allocator lock ordering.
- Local and global quota structures are kept consistent by syncing global qtree state and then writing the node-local dquot entry.
- Last-reference release can be delayed from the downconvert thread because taking quota locks there could block cluster lock recovery.
