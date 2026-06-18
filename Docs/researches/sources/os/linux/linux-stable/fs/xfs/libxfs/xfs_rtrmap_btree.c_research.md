# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrmap_btree.c

## Purpose

Implements the realtime reverse mapping btree. This btree maps realtime physical extents back to owners and is rooted in an rtgroup metadata inode.

## Main Responsibilities

- Defines `xfs_rtrmapbt_ops`, an inode-rooted overlapping btree for realtime reverse mappings.
- Implements key creation, high-key creation, record packing, comparisons, and contiguity tests.
- Verifies realtime rmap btree blocks through `xfs_rtrmapbt_buf_ops`.
- Supports optional in-memory realtime rmap btrees under `CONFIG_XFS_BTREE_IN_MEM`.
- Converts root blocks between on-disk dinode fork format and in-memory btree-root format.
- Computes max records, max levels, and reservations.
- Creates empty realtime rmap metadata inodes.
- Initializes rmap records for the realtime superblock extent.
- Reports the highest realtime group block covered by the rmap tree.

## Important Functions

- `xfs_rtrmapbt_init_cursor`
- `xfs_rtrmapbt_commit_staged_btree`
- `xfs_rtrmapbt_maxrecs`
- `xfs_rtrmapbt_compute_maxlevels`
- `xfs_rtrmapbt_calc_reserves`
- `xfs_iformat_rtrmap`
- `xfs_rtrmapbt_to_disk`
- `xfs_iflush_rtrmap`
- `xfs_rtrmapbt_create`
- `xfs_rtrmapbt_init_rtsb`
- `xfs_rtrmap_highest_rgbno`

## Important Invariants

- Realtime rmap btrees require rmapbt support.
- The btree is overlapping: internal nodes store low and high keys per pointer.
- Written/unwritten state is a record attribute, not part of key comparison.
- Inode-root format uses `XFS_DINODE_FMT_META_BTREE`.
- Reflink-capable realtime rmap trees can theoretically have extreme sharing, so max-level computation falls back to data-device space limits.

## Optional In-Memory Support

When `CONFIG_XFS_BTREE_IN_MEM` is enabled, this file defines:
- `xfs_rtrmapbt_mem_ops`
- `xfs_rtrmapbt_mem_cursor`
- `xfs_rtrmapbt_mem_init`

This allows generated or repair-time realtime rmap btrees to exist in memory even if the on-disk feature is not enabled.

## Dependencies

- Uses generic btree, btree staging, and memory-btree infrastructure.
- Coupled to `xfs_rtgroup` for rtgroup ownership.
- Uses rmap record/key encoding from common XFS rmap code.
- Reservation calculations in `xfs_trans_resv.c` depend on this btree’s max-level fields.

## Research Notes

This file is the realtime counterpart to the data-device rmap btree but differs in two major ways: it is inode-rooted, and it supports realtime group metadata ownership. The overlapping-key logic is central to correctness.
