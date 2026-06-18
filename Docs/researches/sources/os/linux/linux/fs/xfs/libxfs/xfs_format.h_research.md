# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_format.h

## Purpose

`xfs_format.h` is the central XFS on-disk format contract. It defines the packed/be-endian structures, magic numbers, feature bits, size limits, conversion helpers, and btree record layouts that all XFS kernel and userspace libxfs code must interpret consistently.

## Main Content

- Defines superblock formats:
  - In-core `struct xfs_sb`.
  - On-disk `struct xfs_dsb`.
  - V1-V5 version fields and older `sb_versionnum` feature bits.
  - V5 feature masks for compat, read-only compat, incompat, and log-incompat features.
  - Recent incompat features include parent pointers, metadata directory tree, zoned realtime allocator, and realtime group LBA gaps.
- Defines geometry and address conversion macros:
  - FSB/basic-block/byte conversions.
  - AG block/address conversions.
  - Inode number decomposition and composition macros.
- Defines allocation group headers:
  - `struct xfs_agf` for free-space metadata.
  - `struct xfs_agi` for inode allocation metadata.
  - `struct xfs_agfl` for AG freelist blocks.
  - Logging bitmasks for AGF and AGI fields.
- Defines realtime metadata:
  - Realtime bitmap/summary word unions.
  - Realtime group limits and `struct xfs_rtsb`.
  - Realtime btree root formats for rmap and refcount metadata.
- Defines timestamp encoding:
  - Legacy signed 32-bit seconds + nanoseconds.
  - Bigtime unsigned 64-bit nanosecond encoding with epoch conversion helpers.
  - Quota bigtime conversion and bounds.
- Defines on-disk inode core:
  - `struct xfs_dinode`, inode fork pointer/size helpers, device encoding helpers.
  - Inode format enum values.
  - Legacy and V3 inode fields, CRC, creation time, UUID, large extent counts, metadata inode type.
  - `di_flags` and `di_flags2`, including realtime, reflink, DAX, bigtime, nrext64, and metadata inode bits.
- Defines btree record formats:
  - Free-space btrees: allocation by block and by count.
  - Inode allocation btrees: inobt and finobt records, sparse inode holemasks, free masks.
  - Reverse mapping btree records and owner constants.
  - Refcount btree records and CoW staging flag.
  - Bmap btree records and delayed allocation startblock helpers.
  - Generic btree block short/long headers and CRC offsets.
- Defines quota, remote symlink, ACL, and xattr constants.

## Key Interfaces and Invariants

- V5 filesystems use expanded feature fields and CRC-protected metadata. Many helpers test feature bits by reading `struct xfs_sb`.
- AGI fields are split into logging regions because the unlinked inode hash table sits in the middle of the structure.
- Inode allocation records represent 64 inodes per chunk. Sparse inode chunks use a 16-bit holemask, with each bit covering multiple inodes.
- The format intentionally preserves old layout quirks such as `sb_bad_features2`.
- Structures are endian-annotated and generally must remain padded/aligned as on disk.
- `xfs_ialloc.c` and `xfs_ialloc_btree.c` depend directly on the inobt/finobt constants, AGI layout, and logging bit definitions from this file.

## Dependencies

This header assumes fundamental XFS scalar types and feature predicates are available from surrounding libxfs/kernel headers. It is included by most libxfs implementation files and is foundational for both kernel and xfsprogs-compatible code.
