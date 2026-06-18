# File Research: sources/os/linux/linux-stable/fs/minix/inode.c

## Purpose

Implements MINIX filesystem superblock setup, inode lifecycle, inode disk encoding/decoding, page-cache address-space operations, and module registration. It is the central mount/inode glue for MINIX V1, V2, and V3 formats.

## Main Entry Points

- `minix_fill_super()`: reads and validates the on-disk superblock, loads inode/zone bitmaps, detects V1/V2/V3 layout, and creates the root dentry.
- `minix_reconfigure()`: handles read-only/read-write remount state transitions.
- `minix_iget()`: loads an inode through the V1 or V2/V3 raw inode formats.
- `minix_write_inode()`: writes V1 or V2/V3 inode metadata back to disk.
- `minix_set_inode()`: assigns file, directory, symlink, or special-file operation tables.
- `minix_get_block()`, `minix_writepages()`, `minix_read_folio()`, `minix_write_begin()`: connect MINIX block mapping to generic buffered I/O.
- `minix_truncate()`: dispatches truncation to the version-specific indirect-tree implementation.
- `init_minix_fs()` / `exit_minix_fs()`: create the inode cache and register/unregister the filesystem type.

## Control Flow And State

Mounting allocates `minix_sb_info`, forces the initial MINIX block size, reads block 1, detects the magic/version, sets name length and directory entry size, validates zone and bitmap geometry, reads imap/zmap blocks, marks bitmap bit zero allocated, and then reads `MINIX_ROOT_INO`. Read-write mounts clear the valid-state flag for V1/V2 filesystems and restore it on unmount/remount read-only. V3 has different state handling and supports a superblock-provided block size.

Inode loading branches by `INODE_VERSION()`. V1 inodes use a single timestamp, 16-bit zones, and old device encoding; V2/V3 use separate atime/mtime/ctime and 32-bit zones. Writeback mirrors those layouts and synchronously flushes the raw inode buffer for `WB_SYNC_ALL`.

Address-space operations use the generic block helpers plus MINIX `get_block`, and failed extending writes truncate page cache and filesystem blocks back to `i_size`. Eviction truncates unlinked inodes, synchronizes metadata buffer heads for linked inodes, invalidates tracked metadata buffers, clears the VFS inode, and frees the on-disk inode if link count reached zero.

## Dependencies

Depends on `minix.h`, MINIX bitmap/block/inode allocation helpers, the V1/V2 indirect-tree wrappers, Linux buffer-head and mpage helpers, fs_context block-device mounting, generic inode/page-cache helpers, and the VFS file/directory operation tables declared elsewhere in the MINIX driver.

## Risks

Correctness is dominated by legacy on-disk format handling: magic detection, V1 maximum size limits, bitmap block sufficiency, old device encoding, and V1/V2/V3 state differences. The mount path has many partial-allocation exits and must release bitmap buffers and superblock buffers in the right order. Metadata consistency depends on `mapping_metadata_bhs` tracking indirect blocks dirtied by truncation/allocation.
