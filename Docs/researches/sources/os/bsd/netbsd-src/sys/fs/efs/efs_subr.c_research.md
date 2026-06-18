# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_subr.c

Read completely: 623 lines.

Provides EFS support routines for superblock validation, inode reads, byte-order conversion, directory lookup, extent conversion, and extent iteration. It owns the global `efs_inode_pool`.

`efs_sb_checksum()` implements SGI’s old/new checksum variants over the superblock. `efs_sb_validate()` checks magic, checksum, maximum size, first cylinder group, and basic nonzero geometry/bitmap fields. `efs_locate_inode()` maps an inode number to a cylinder-group inode block and index, and `efs_read_inode()` reads the containing block and copies the target dinode.

`efs_sync_dinode_to_inode()` converts big-endian disk inode fields to host-order cached fields. The inverse `efs_sync_inode_to_dinode()` panics because this implementation is effectively read-only. Under diagnostics, `efs_is_inode_synced()` checks cache consistency.

Directory lookup walks EFS directory blocks through extents: `efs_dirblk_lookup()` scans slots, compares component names, and returns a big-endian decoded inode; `efs_extent_lookup()` reads each directory block in an extent; `efs_inode_lookup()` iterates all directory extents. Extent conversion helpers decode/encode the 24-bit packed extent fields, and the iterator supports direct extents, indirect extent vectors, optional start hints, and binary search into indirect extents.
