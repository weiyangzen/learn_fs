# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrefcount_btree.c

## Purpose

Implements the realtime refcount btree. This btree tracks sharing reference counts for extents on the realtime device and is rooted in an rtgroup metadata inode.

## Main Responsibilities

- Defines `xfs_rtrefcountbt_ops`, the btree operation table for inode-rooted realtime refcount btrees.
- Implements key, high-key, record, and pointer initialization.
- Implements cursor allocation through `xfs_rtrefcountbt_init_cursor`.
- Verifies realtime refcount btree blocks through `xfs_rtrefcountbt_buf_ops`.
- Converts root blocks between on-disk dinode fork format and in-memory btree-root format.
- Computes max records, max levels, and reservation sizes.
- Creates empty realtime refcount btree metadata inodes.

## Important Functions

- `xfs_rtrefcountbt_init_cursor`
- `xfs_rtrefcountbt_commit_staged_btree`
- `xfs_rtrefcountbt_maxrecs`
- `xfs_rtrefcountbt_compute_maxlevels`
- `xfs_rtrefcountbt_calc_reserves`
- `xfs_iformat_rtrefcount`
- `xfs_rtrefcountbt_to_disk`
- `xfs_iflush_rtrefcount`
- `xfs_rtrefcountbt_create`

## Important Invariants

- Realtime refcount btrees require reflink support.
- The btree is inode-rooted and uses `XFS_DINODE_FMT_META_BTREE`.
- Root blocks in the inode fork have a compact on-disk format; in-memory roots use normal btree block layout.
- Refcount keys are ordered by encoded startblock, including refcount domain.
- The maximum height is constrained both by data-device block availability and realtime group extent count.

## Dependencies

- Uses generic btree cursor and staging infrastructure.
- Uses refcount record definitions from shared XFS metadata formats.
- Coupled to `xfs_rtgroup` for the owning rtgroup and refcount inode.
- Used by transaction reservation code to size realtime refcount update transactions.

## Research Notes

This file mirrors much of the data-device refcount btree logic but adapts it for metadata inodes and realtime groups. The root conversion code is especially important because the dinode fork layout differs from the normal incore btree block layout.
