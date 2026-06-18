# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrefcount_btree.h

## Purpose

Declares the realtime refcount btree API and provides inline address/space helpers for records, keys, pointers, and inode-root formats.

## Main API

- Cursor and staging:
  - `xfs_rtrefcountbt_init_cursor`
  - `xfs_rtrefcountbt_stage_cursor`
  - `xfs_rtrefcountbt_commit_staged_btree`
- Geometry:
  - `xfs_rtrefcountbt_maxrecs`
  - `xfs_rtrefcountbt_compute_maxlevels`
  - `xfs_rtrefcountbt_droot_maxrecs`
  - `xfs_rtrefcountbt_maxlevels_ondisk`
- Cache lifecycle:
  - `xfs_rtrefcountbt_init_cur_cache`
  - `xfs_rtrefcountbt_destroy_cur_cache`
- Reservation sizing:
  - `xfs_rtrefcountbt_calc_reserves`
  - `xfs_rtrefcountbt_calc_size`
- Inode formatting:
  - `xfs_iformat_rtrefcount`
  - `xfs_rtrefcountbt_to_disk`
  - `xfs_iflush_rtrefcount`
  - `xfs_rtrefcountbt_create`

## Inline Layout Helpers

The header defines address helpers for:
- incore btree root records
- incore btree root keys
- incore btree root pointers
- on-disk dinode-root records
- on-disk dinode-root keys
- on-disk dinode-root pointers

It also computes:
- incore root space
- on-disk root space
- root space from existing root blocks

## Important Invariants

- `XFS_RTREFCOUNT_BLOCK_LEN` uses CRC long btree block header size.
- Leaf roots store refcount records.
- Internal roots store key-pointer pairs.
- On-disk roots use `struct xfs_rtrefcount_root`, which is smaller than an incore btree block.

## Research Notes

This header is layout-sensitive. Userspace tools also rely on some helpers that may appear unused in the kernel build.
