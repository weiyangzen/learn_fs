# File Research: sources/os/linux/linux/fs/hfs/hfs_fs.h

Purpose: Main classic HFS internal header defining in-core inode/superblock state, flags, helpers, time conversion, and module-wide function prototypes.

Key structures and helpers:
- `struct hfs_inode_info` stores open count, flags, catalog key, resource fork link, extent cache, allocation sizing, physical size, and embedded VFS inode.
- `struct hfs_sb_info` stores MDB buffers, bitmap, catalog/extents trees, counts, mount options, NLS tables, dirty flags, and delayed MDB work.
- `HFS_I()` and `HFS_SB()` convert generic VFS objects to HFS-private data.
- Time helpers convert between Mac epoch timestamps and Linux `timespec64`, using global timezone adjustment.
- `sb_bread512()` reads a 512-byte-sector address through the current block size and returns the sector data pointer.

Dependencies and integration:
- Declares APIs for bitmap, catalog, extents, inode, MDB, partition, string, translation, and superblock code.
- Includes Linux buffer/page/cache, FS, workqueue, NLS-facing support via dependent files.

Risk notes:
- Time conversion intentionally preserves historical HFS/Linux behavior, including global timezone effects.
- Many filesystem counters are stored as atomics in memory but written as 32-bit on-disk values, so overflow checks matter.
