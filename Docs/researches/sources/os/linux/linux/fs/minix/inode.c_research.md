# File Research: sources/os/linux/linux/fs/minix/inode.c

## Purpose
Implements the Minix filesystem superblock lifecycle, inode cache, inode read/write translation, page-cache address-space operations, and module registration. It is the central glue between the Linux VFS and Minix V1/V2/V3 on-disk metadata.

## Main Responsibilities
- Mount-time superblock parsing and validation for Minix V1, V2, and V3.
- Bitmap buffer loading for inode and zone maps.
- Root inode lookup and superblock operation installation.
- In-core inode allocation/freeing through `minix_inode_cache`.
- Inode eviction, truncation, free-on-last-link, and metadata buffer synchronization.
- Read/write conversion between Linux `struct inode` and Minix V1/V2 disk inode formats.
- Address-space operations for buffered reads, writes, writeback, bmap, migration, and noop direct I/O.
- Filesystem module registration through `minix_fs_type`.

## Key Functions
- `minix_fill_super()` reads block 1, detects Minix magic/version, initializes `minix_sb_info`, loads imap/zmap blocks, validates geometry, installs `minix_sops`, and creates the root dentry.
- `minix_check_superblock()` rejects unsupported zone sizes, bad inode/data-zone geometry, insufficient bitmap blocks, and invalid V1 maximum size.
- `minix_reconfigure()` handles read-only/read-write remount transitions and preserves/restores legacy `s_state`.
- `minix_put_super()` releases bitmap buffers, superblock buffer, and `minix_sb_info`.
- `minix_evict_inode()` truncates deleted inodes, syncs metadata buffers for live inodes, invalidates Minix metadata buffer tracking, and frees unlinked inodes.
- `minix_get_block()` dispatches block mapping to `V1_minix_get_block()` or `V2_minix_get_block()`.
- `minix_set_inode()` assigns file, directory, symlink, or special-file operations according to inode mode.
- `V1_minix_iget()` / `V2_minix_iget()` load raw on-disk inode fields into VFS inodes.
- `V1_minix_update_inode()` / `V2_minix_update_inode()` write VFS inode fields back into raw Minix inode formats.
- `minix_write_inode()` synchronizes raw inode buffers, including synchronous writeback error detection.
- `minix_getattr()` fills stat data and computes block counts through version-specific block-count helpers.
- `minix_truncate()` dispatches truncation to V1 or V2/V3 indirect-tree implementations.

## Data and Control Flow
Mounting starts with `minix_get_tree()` calling `get_tree_bdev()`, which invokes `minix_fill_super()`. The superblock parser first assumes the old Minix superblock layout, then switches to Minix3 parsing if the V3 magic is present at offset 24. After version detection, it allocates a combined bitmap buffer pointer array, reads all inode and zone bitmap blocks, reserves bit zero in both maps, and fetches `MINIX_ROOT_INO`.

Inode lookup uses `iget_locked()`, then delegates raw inode loading by filesystem version. Inode operation tables and file operation tables are assigned after raw mode and device data are loaded.

Buffered file I/O uses generic block helpers with Minix block mapping. `minix_write_begin()` calls `block_write_begin()` and rolls back failed extension writes by truncating page cache and filesystem blocks.

## Important Behaviors and Edge Cases
- V3 uses its own block size and has no mutable `s_state` in the same way as V1/V2.
- V1 maximum file size is explicitly checked against the indirect-tree mapping limit.
- Deleted raw inodes with zero links are treated as stale and fail with `-ESTALE`.
- Character/block device inodes store old-style encoded device numbers in `i_zone[0]`.
- Symlink inodes use `page_get_link` and `inode_nohighmem()`.
- `minix_getattr()` intentionally uses `nop_mnt_idmap`, so stat ownership is not remapped here.
- Mounting read-write clears legacy `MINIX_VALID_FS` until unmount/remount read-only.

## Dependencies
- Internal Minix declarations from `minix.h`.
- Block and buffer helpers from `buffer_head`, `mpage`, and generic block mapping code.
- Minix bitmap/inode allocators from sibling Minix source files.
- VFS mount API through `fs_context` and `get_tree_bdev()`.

## Research Notes
This file is the Minix filesystem integration point. The actual block tree algorithms are in `itree_common.c` with V1/V2 wrappers, while directory operations are in `namei.c`. The file is conservative and legacy-oriented: fixed V1/V2 structures, old device encoding, and explicit validation around ancient filesystem geometry.
