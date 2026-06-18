# File Research: sources/os/linux/linux-stable/fs/ocfs2/journal.h

Purpose: defines OCFS2 journal state structures, transaction/checkpoint inline helpers, journal/recovery/orphan-scan APIs, journal access prototypes, transaction access constants, and journal credit calculations for metadata operations.

Read coverage: complete file read, 610 lines.

Key structures and constants:
- `enum ocfs2_journal_state` distinguishes free, loaded, and shutdown journals.
- `struct ocfs2_journal` stores the JBD2 journal pointer, journal inode, owning OCFS2 superblock, journal dinode buffer, outstanding transaction count, transaction barrier, checkpoint waitqueue, local-alloc cleanup list, recovery work item, and OCFS2 transaction id.
- `struct ocfs2_recovery_map` is a flexible array of node numbers pending recovery.
- `OCFS2_JOURNAL_ACCESS_CREATE`, `WRITE`, and `UNDO` identify access intent for JBD2.
- Credit constants and inline calculators cover inode updates, xattr updates, quota writes/syncs, group extend/add, suballocator alloc/free, truncate log, directory operations, mknod/link/unlink/rename, orphan add/remove, xattr block creation, dx index updates, refcount tree operations, extent extension, symlink writes, and block group allocation.

Major logic:
- `ocfs2_inc_trans_id()` increments journal transaction ids with wraparound avoidance so zero is never used.
- `ocfs2_set_ci_lock_trans()` records the current transaction id in a metadata cache object so lock downconversion can determine checkpoint safety.
- `ocfs2_ci_fully_checkpointed()` tests whether a metadata cache object's last transaction is older than the journal's checkpointed transaction id.
- `ocfs2_ci_is_new()` tracks metadata that has not yet reached disk and clears `ci_created_trans` after checkpoint.
- `ocfs2_checkpoint_inode()` wakes the commit thread and waits until an inode metadata cache is fully checkpointed on clustered mounts.
- Ordered-data helpers wrap JBD2 ranged inode write and ordered truncate for OCFS2's embedded `ip_jinode`.
- `ocfs2_update_inode_fsync_trans()` records the transaction id needed by fsync/fdatasync unless the handle is aborted.

Declared APIs:
- Journal lifecycle/recovery: `ocfs2_journal_alloc()`, `ocfs2_journal_init()`, `ocfs2_journal_load()`, `ocfs2_journal_shutdown()`, `ocfs2_journal_wipe()`, `ocfs2_check_journals_nolocks()`, `ocfs2_recovery_thread()`, `ocfs2_mark_dead_nodes()`, `ocfs2_complete_mount_recovery()`, `ocfs2_complete_quota_recovery()`.
- Orphan scan: `ocfs2_orphan_scan_init()`, `ocfs2_orphan_scan_start()`, `ocfs2_orphan_scan_stop()`.
- Transaction: `ocfs2_start_trans()`, `ocfs2_commit_trans()`, `ocfs2_extend_trans()`, `ocfs2_assure_trans_credits()`, `ocfs2_allocate_extend_trans()`.
- Journal access wrappers for dinodes, extent blocks, refcount blocks, group descriptors, xattr blocks, quota blocks, directory blocks, dx roots, dx leaves, and no-ECC buffers.

Concurrency and lifetime:
- Transaction id helpers use global `trans_inc_lock`.
- `ocfs2_checkpoint_inode()` waits on `journal->j_checkpointed` and is skipped on local mounts.
- Credit calculators are conservative; callers still need matching locks, allocator reservations, and journal access/dirty calls.

Important dependencies:
- Includes Linux JBD2 and VFS headers and depends on OCFS2 inode/cache accessors, superblock feature tests, extent metadata sizing, block/cluster conversion helpers, and quota feature state.

Risk and edge cases:
- Metadata lock downconversion relies on correct `ci_last_trans` and transaction id increments; missing journal access markers can release locks before checkpoint.
- Credit math is intentionally maximum-oriented; under-reserving credits in callers can force transaction restarts in lock-sensitive code.
- `ocfs2_calc_extend_credits()` assumes the passed extent list is the root extent list.
- `ocfs2_update_inode_fsync_trans()` dereferences the active transaction; callers must pass a valid, non-stopped handle.
