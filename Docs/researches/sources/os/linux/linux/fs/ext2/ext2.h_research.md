# File Research: sources/os/linux/linux/fs/ext2/ext2.h

Read status: complete, 820 lines.

This header defines ext2’s in-memory structures, on-disk structures, constants, feature bits, mount flags, ioctl numbers, helper macros, and cross-file prototypes.

Key responsibilities:
- Defines ext2 block number types and `E2FSBLK` format.
- Defines reservation-window structures used by `balloc.c`.
- Defines `struct ext2_sb_info`, the in-core superblock state.
- Defines `struct ext2_group_desc`, `struct ext2_inode`, `struct ext2_super_block`, and directory entry structures.
- Defines inode flags, mount flags, default options, feature bits, special inode numbers, and directory record sizing macros.
- Declares functions shared among ext2 implementation files.
- Provides helpers for block group first/last block numbers and little-endian bitmap operations.

Important structures:
- `ext2_sb_info`: group sizing, descriptor buffers, mount options, counters, blockgroup locks, reservation tree, xattr cache, DAX device info, and superblock buffer.
- `ext2_inode_info`: ext2-specific inode block pointers, flags, ACL/xattr fields, deletion time, block group, reservation info, lookup hint, xattr semaphore, metadata lock, truncate mutex, orphan list, quota pointers, and metadata buffer tracking.
- `ext2_super_block`: on-disk ext2 superblock including counts, geometry, mount/check metadata, revision, feature bits, UUID/name, journal compatibility fields, hash seed, and defaults.
- `ext2_inode`: on-disk inode layout including mode, UID/GID, size, timestamps, block pointers, generation, ACL fields, fragments, and OS-dependent fields.

Key feature definitions:
- Supported compatible feature: ext attrs.
- Supported incompatible features: filetype and meta_bg.
- Supported readonly-compatible features: sparse super, large file, and btree dir.
- Mount flags include old allocator, grpid, error policy, xattrs, ACL, quota, reservation, and DAX.

Concurrency notes:
- `s_lock` protects mount state and selected superblock fields.
- `truncate_mutex` serializes truncate against block mapping and protects reservation internals.
- `i_meta_lock` protects indirect block tree metadata checks/updates.
- Block group locks protect group bitmap/count mutation.

Research notes:
- This header is the central contract for ext2 implementation files.
- It preserves the historical ext2 on-disk ABI while adapting to modern VFS APIs such as iomap, DAX, folios, file attributes, ACLs, and quota.
