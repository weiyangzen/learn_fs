# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr_remote.c

## Purpose

`xfs_attr_remote.c` manages out-of-line extended attribute values stored in blocks mapped by the inode attr fork. It computes remote block counts, stamps and verifies CRC remote headers, reads and writes remote value buffers, finds allocation holes, steps delayed allocation, invalidates cached buffers, and removes remote extents.

## Main Behavior

Remote attr value buffers are intentionally kept out of the logging system because CRC-enabled remote blocks can require buffers larger than the maximum logged metadata buffer. CRC-enabled remote blocks reserve space for `struct xfs_attr3_rmt_hdr`; non-CRC filesystems use the whole attr block for data. `xfs_attr3_rmt_blocks` accounts for the per-block header overhead when calculating storage needs.

Read verification checks CRC, magic, uuid, physical block number, per-block byte count, offset bounds, and nonzero owner. Copy-out additionally verifies the expected owner, offset, size, and block number before copying payload data to the caller. Write paths stamp headers with magic, offset, byte count, uuid, owner, physical block number, and `NULLCOMMITLSN`, then synchronously write buffers.

`xfs_attr_rmtval_get` walks attr fork mappings, reads mapped blocks with remote buffer ops, remaps disk `-ENODATA` to `-EIO`, and copies payload out. `xfs_attr_rmt_find_hole` finds address space for a remote value, while `xfs_attr_rmtval_find_space` stores that plan in a delayed attr intent. `xfs_attr_rmtval_set_blk` allocates one mapped extent for delayed operations, and `xfs_attr_rmtval_set_value` writes the already allocated value blocks.

Removal is split between cache invalidation and extent unmapping. `xfs_attr_rmtval_invalidate` marks incore remote buffers stale before unmap, and `xfs_attr_rmtval_remove` calls `xfs_bunmapi`, returning `-EAGAIN` until all extents are removed.

## Dependencies and Risks

This file depends on bmap mapping/unmapping, attr fork geometry, buffer verification, synchronous buffer writes, delayed attr intents, health marking, and remote leaf entries from `xfs_attr_leaf.c`. Correctness depends on remote buffers never being logged, header fields matching physical storage and owner metadata, stale buffers being invalidated before reuse, and leaf entries remaining incomplete until allocation and synchronous write completion.
