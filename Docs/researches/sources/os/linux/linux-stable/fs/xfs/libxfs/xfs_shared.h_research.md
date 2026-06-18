# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_shared.h

## Purpose

Collects declarations and definitions shared across kernel and userspace libxfs that do not fit better in more specialized shared headers.

## Main Contents

- External declarations for buffer verifier operations:
  - AG headers
  - attribute blocks
  - bmbt
  - dquot
  - inode buffers
  - refcount/rmap btrees
  - realtime bitmap/summary buffers
  - realtime superblock
  - realtime rmap/refcount btrees
  - superblock
  - symlink buffers
- External declarations for btree operation tables.
- Inline btree-op classifiers:
  - allocation btrees
  - inode btrees
  - bmap btree
  - refcount btree
  - rmap btree
  - realtime rmap btree
  - realtime refcount btree
  - optional in-memory rmap variants
- Transaction flag definitions.
- Superblock modification field masks.
- Buffer cache reference priority constants.
- `struct xfs_ino_geometry`.

## Important Invariants

- `XFS_TRANS_RTBITMAP_LOCKED` records realtime bitmap/summary locking state.
- `XFS_TRANS_SB_RGCOUNT` is a transaction superblock modification mask for realtime group count updates.
- In-memory btree classifiers depend on `CONFIG_XFS_BTREE_IN_MEM`.
- Buffer reference constants tune cache pressure for metadata buffers.

## Research Notes

This file is glue for libxfs-wide metadata dispatch. New btree types such as realtime rmap/refcount must be declared here so generic code can identify operation tables and verifier ops.
