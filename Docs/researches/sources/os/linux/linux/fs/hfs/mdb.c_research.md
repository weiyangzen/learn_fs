# File Research: sources/os/linux/linux/fs/hfs/mdb.c

Purpose: Reads, validates, updates, and releases the classic HFS Master Directory Block, allocation bitmap, alternate MDB, and B-tree roots.

Key functions:
- `hfs_get_last_session()` handles CD-ROM multisession/session mount selection.
- `is_hfs_cnid_counts_valid()` checks next CNID, file count, and folder count fit in 32-bit on-disk fields.
- `hfs_mdb_get()` locates the HFS MDB, optionally via partition map, sets block size, reads volume metadata/bitmap, opens extents/catalog B-trees, and marks unsafe volumes read-only.
- `hfs_mdb_commit()` writes dirty MDB counters, alternate MDB fork metadata, and allocation bitmap changes.
- `hfs_mdb_close()` marks a writable volume cleanly unmounted.
- `hfs_mdb_put()` closes B-trees, releases MDB buffers, unloads NLS tables, and frees the bitmap.

Dependencies and integration:
- Uses `hfs_part_find()`, `hfs_btree_open()`, and `hfs_inode_write_fork()`.
- Dirty flags are set by allocation/catalog/inode code and flushed by `super.c`.

Risk notes:
- Mount is forced read-only if counts overflow, the volume was not cleanly unmounted, or it is marked locked.
- Partial initialization failures rely on caller cleanup through `hfs_mdb_put()`, so null-safe release behavior is important.
