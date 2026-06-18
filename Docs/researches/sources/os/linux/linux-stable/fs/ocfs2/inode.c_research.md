# File Research: sources/os/linux/linux-stable/fs/ocfs2/inode.c

Purpose: implements OCFS2 inode cache lookup, on-disk dinode validation, VFS inode population/refresh, inode dirtying, eviction/delete/wipe paths, orphan-aware deletion, filecheck validation/repair reads, and inode-backed metadata-cache operations.

Read coverage: complete file read, 1,815 lines.

Key structures and state:
- `struct ocfs2_find_inode_args` carries block number, VFS inode number, iget flags, and system-file type into `iget5_locked()`.
- `OCFS2_I(inode)` state managed here includes `ip_blkno`, cluster-lock resources, `ip_clusters`, `ip_attr`, `ip_dyn_features`, orphan/recovery flags, metadata cache, extent map, local allocation reservation, and JBD2 inode fsync transaction ids.
- `OCFS2_FI_FLAG_*` controls special iget behavior for system files, orphan recovery, and filecheck check/fix paths.
- Inode lifecycle flags such as `OCFS2_INODE_SYSTEM_FILE`, `OCFS2_INODE_DELETED`, `OCFS2_INODE_MAYBE_ORPHANED`, `OCFS2_INODE_SKIP_ORPHAN_DIR`, and `OCFS2_INODE_DIO_ORPHAN_ENTRY` steer deletion and recovery.

Major logic:
- `ocfs2_iget()` validates input block numbers, uses `iget5_locked()` with OCFS2-specific find/init callbacks, reads new inodes from disk, rejects bad inodes, and initializes fsync/datasync transaction ids from the current JBD2 transaction state.
- `ocfs2_init_locked_inode()` sets `i_ino`, `ip_blkno`, and lockdep classes for system-file inodes and quota allocation semaphores.
- `ocfs2_populate_inode()` copies dinode mode, owner, size, timestamps, link count, cluster count, attributes, dynamic features, device id, file operations, inode operations, address-space operations, and OCFS2 lock resources into the VFS inode.
- `ocfs2_read_locked_inode()` optionally takes open/meta cluster locks for non-system inodes, chooses normal or filecheck read/repair validation, handles system-file generation compatibility, writes repaired dirty non-JBD buffers when needed, and marks failures as bad inodes.
- `ocfs2_mark_inode_dirty()` journals dinode access, writes mutable VFS inode state back to the dinode, dirties the metadata buffer, and records fsync transaction ids.
- `ocfs2_refresh_inode()` refreshes in-memory inode fields from a dinode under `ip_lock`.
- `ocfs2_validate_inode_block()` validates metadata ECC, link/mode sanity, dinode signature, block number, valid flag, filesystem generation, suballocator slot, inline-data bounds, chain-list layout, and refcount-root presence.
- Filecheck helpers translate validation failures into `OCFS2_FILECHECK_ERR_*` codes and can repair limited fields: `i_blkno`, filesystem generation, extent-list next-free count, and metadata ECC.
- Delete path starts in `ocfs2_evict_inode()`, then `ocfs2_delete_inode()` blocks signals, takes NFS sync and inode cluster locks, checks DIO orphan state, asks the cluster whether wiping is safe via open-lock trylock, truncates page cache, and calls `ocfs2_wipe_inode()`.
- `ocfs2_wipe_inode()` serializes with orphan recovery, locks the orphan directory when needed, truncates data, removes directory index trees, xattrs, refcount trees, and finally frees the dinode through the inode allocator.
- `ocfs2_clear_inode()` checkpoints outstanding metadata unless the inode was successfully deleted, drops locks and reservations, verifies no pending I/O markers/unwritten extents/cache entries remain, clears inode-private state, and releases the JBD2 inode.

Important entry points:
- Lookup/load: `ocfs2_ilookup()`, `ocfs2_iget()`, `ocfs2_read_inode_block()`, `ocfs2_read_inode_block_full()`.
- VFS state sync: `ocfs2_populate_inode()`, `ocfs2_refresh_inode()`, `ocfs2_mark_inode_dirty()`, `ocfs2_inode_revalidate()`.
- Lifecycle: `ocfs2_evict_inode()`, `ocfs2_sync_blockdev()`.
- Validation/cache: `ocfs2_validate_inode_block()`, `ocfs2_inode_caching_ops`.

Concurrency and lifetime:
- Cluster meta/open locks protect trusted dinode reads and deletion decisions; some system/recovery paths intentionally avoid locks to prevent mount-time and orphan-recovery deadlocks.
- `ip_lock` protects in-memory OCFS2 inode fields mirrored into dinodes.
- Delete uses NFS sync locks, inode cluster locks, orphan-dir locks, open-lock conversion, and orphan-recovery state bits to prevent two nodes from truncating or freeing the same inode.
- `ocfs2_clear_inode()` waits for checkpointing before dropping lock resources so remote nodes do not see uncheckpointed metadata as stable.
- Metadata cache callbacks lock with `ip_lock` and serialize I/O with `ip_io_mutex`.

Important dependencies:
- Uses OCFS2 DLM glue, journaling, extent map, file operations, directory/orphan helpers, xattr removal, refcount tree removal, suballocator dinode free, heartbeat/orphan recovery state, block ECC, and buffer-head I/O.
- Uses VFS inode lifecycle, quota APIs, page-cache truncation/writeback, and JBD2 inode tracking.

Risk and edge cases:
- Dinode validation distinguishes local ECC/block corruption from fatal filesystem metadata inconsistencies; callers must preserve that distinction.
- System-file iget flags must match on-disk `OCFS2_SYSTEM_FL`; mismatches are treated as code bugs.
- Orphan deletion has several intentional early exits: root inode, system files, downconvert thread context, active remote open locks, DIO orphan entries, and concurrent orphan recovery.
- Filecheck repair is deliberately narrow and refuses readonly, in-JBD, invalid-signature, and invalid-valid-flag cases.
- `ocfs2_wipe_inode()` must eventually signal orphan wipe completion after it increments orphan wipe counters or orphan recovery can wait indefinitely.
- Dirty buffer repair in read path may upgrade to an exclusive lock before writing a non-JBD dirty dinode.
