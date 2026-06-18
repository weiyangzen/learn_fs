# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrefcount_btree.h

## Purpose

`xfs_rtrefcount_btree.h` declares realtime refcount btree APIs and layout helpers for in-core and on-disk inode-rooted realtime refcount btree roots.

## Main Content

- Defines `XFS_RTREFCOUNT_BLOCK_LEN` as the CRC long btree block header length.
- Declares live/staged cursor, staged commit, max-record, max-level, reserve, and create helpers.
- Provides inline address helpers for in-core records, keys, and pointers.
- Provides inline address helpers for on-disk dinode-root records, keys, and pointers.
- Provides pointer lookup for in-core roots when only the block size is known.
- Provides size calculators for:
  - In-core btree roots.
  - On-disk root blocks.
  - In-core root size from on-disk root state.
  - On-disk root size from in-core root state.
- Declares inode format/load, disk conversion, and flush helpers.

## Key Interfaces and Invariants

- Some address helpers are kept for userspace even when not used in the kernel file.
- In-core root size includes `XFS_RTREFCOUNT_BLOCK_LEN`; on-disk root size includes `struct xfs_rtrefcount_root`.
- Non-leaf root entries contain key/pointer pairs; leaf roots contain records.
- Root size helpers must be used consistently to avoid overfilling the inode data fork.

## Dependencies

Depends on realtime refcount on-disk structures from `xfs_format.h`, btree cursor types, realtime group types, and inode/dinode definitions supplied by surrounding XFS headers.
