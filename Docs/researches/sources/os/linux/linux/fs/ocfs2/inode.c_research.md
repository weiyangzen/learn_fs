# File Research: sources/os/linux/linux/fs/ocfs2/inode.c

`inode.c` is OCFS2’s core inode lifecycle implementation. It bridges VFS inode objects to on-disk `ocfs2_dinode` records, initializes per-inode lock resources, manages inode cache identity, validates dinode metadata, updates dirty inode state through JBD2 transactions, and owns eviction/delete behavior.

Main responsibilities:
- Maps OCFS2 on-disk inode flags to VFS inode flags with `ocfs2_set_inode_flags()` and back with `ocfs2_get_inode_flags()`.
- Implements `ocfs2_iget()`/`ocfs2_ilookup()` using `iget5_locked()`, custom find/init actors, and block-number based inode identity.
- Populates VFS inode fields from `ocfs2_dinode` in `ocfs2_populate_inode()`, including mode-specific `i_op`, `i_fop`, address-space ops, timestamps, link count, size, sector count, system-file flags, bitmap/quota flags, and lock resource initialization.
- Reads locked inodes with optional cluster locking. It avoids metadata locks for system files, orphan recovery, and local mounts, and supports filecheck check/fix modes through specialized dinode validation/repair.
- Deletes and wipes orphaned inodes. The delete path coordinates inode meta locks, open locks, orphan directory locks, NFS sync lock, truncate, directory index removal, xattr removal, refcount-tree removal, quota release, dinode freeing, and inode allocation bitmap updates.
- Coordinates with orphan recovery by tracking `osb_recovering_orphan_dirs` and `osb_orphan_wipes` so delete_inode and recovery do not deadlock or double-wipe the same inode.
- Maintains eviction behavior through `ocfs2_evict_inode()`, `ocfs2_delete_inode()`, and `ocfs2_clear_inode()`, including checkpointing metadata before lock resources and caches are destroyed.
- Provides `ocfs2_inode_revalidate()` for getattr-style coherency by taking and dropping the inode metadata lock.
- Writes VFS inode state back into dinode buffers via `ocfs2_mark_inode_dirty()`, including size, uid/gid, mode, link count, timestamps, cluster count, dynamic features, and fsync transaction tracking.
- Refreshes in-memory inodes from disk with `ocfs2_refresh_inode()`.
- Validates dinode blocks in `ocfs2_validate_inode_block()`, checking ECC, valid signature, block number, `OCFS2_VALID_FL`, filesystem generation, suballocator slot range, inline-data consistency, chain-list consistency, and refcount-location consistency.
- Implements filecheck-specific validation/repair helpers that return OCFS2 filecheck error classes and can repair limited fields such as `i_blkno`, filesystem generation, extent-list `l_next_free_rec`, and metadata ECC.
- Exposes inode-backed metadata cache operations through `ocfs2_inode_caching_ops`.

Important dependencies:
- Cluster locking: `dlmglue.h` functions such as `ocfs2_inode_lock()`, `ocfs2_open_lock()`, `ocfs2_try_open_lock()`, and lock resource init/free helpers.
- Journaling: `ocfs2_start_trans()`, `ocfs2_journal_access_di()`, `ocfs2_journal_dirty()`, `ocfs2_commit_trans()`, `ocfs2_checkpoint_inode()`.
- Allocation/suballocation: inode allocator system files, `ocfs2_free_dinode()`, truncate log, orphan dirs, quota credits.
- Data/metadata cleanup: xattrs, refcount tree, directory index truncation, extent map truncation, metadata cache shutdown.

Key invariants:
- Inode cache identity is the dinode block number, not just VFS inode number.
- OCFS2 does not trust inode metadata without appropriate cluster locking except in controlled system-file/recovery/read-only paths.
- System files are never deleted through normal inode eviction.
- A zero-link inode is only wiped if the cluster-wide open-lock trylock proves no node still has it live.
- Successfully wiped inodes set `OCFS2_INODE_DELETED`, allowing clear-inode to skip checkpointing metadata that now belongs back to allocator structures.
