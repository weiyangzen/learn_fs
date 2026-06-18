# File Research: sources/os/linux/linux-stable/fs/hfs/mdb.c

## Scope

Reads, validates, opens, commits, closes, and releases the classic HFS Master Directory Block (MDB), alternate MDB, allocation bitmap, and core B-trees.

## APIs And Behavior

- `hfs_get_last_session()` resolves multisession CD-ROM starts or an explicit session option.
- `is_hfs_cnid_counts_valid()` validates next CNID, file count, and folder count against 32-bit HFS limits.
- `hfs_mdb_get()` sets device block size, finds the MDB directly or through Mac partition maps, validates allocation block size, loads primary and alternate MDBs, loads the volume bitmap, opens extents/catalog B-trees, and forces read-only on corrupt counts, dirty unmount, or locked volume attributes.
- `hfs_mdb_commit()` writes dirty MDB counters/timestamps, optionally syncs the alternate MDB when tree fork extents change, and writes dirty volume bitmap blocks.
- `hfs_mdb_close()` marks a writable volume cleanly unmounted.
- `hfs_mdb_put()` closes B-trees, releases buffers, unloads NLS tables, and frees the bitmap.

## State And Dependencies

This file initializes most `hfs_sb_info` runtime state: allocation geometry, counters, root counts, B-tree pointers, bitmap memory, NLS lifetime, and dirty flags. It depends on `hfs_part_find()`, `hfs_btree_open()`, `hfs_inode_write_fork()`, and block-buffer IO.

## Risks And Invariants

Mount can leave the filesystem read-only based on on-disk state but still complete successfully. Bitmap allocation is fixed at 8192 bytes, matching classic HFS bitmap limits. Commit locks the primary MDB buffer while updating MDB fields and bitmap dirty state, so callers should not hold conflicting buffer locks.
