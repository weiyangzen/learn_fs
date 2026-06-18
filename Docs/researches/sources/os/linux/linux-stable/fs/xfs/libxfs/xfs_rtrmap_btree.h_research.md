# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrmap_btree.h

## Purpose

Declares the realtime rmap btree API and provides inline helpers for incore and on-disk root layout.

## Main API

- Cursor and staging:
  - `xfs_rtrmapbt_init_cursor`
  - `xfs_rtrmapbt_stage_cursor`
  - `xfs_rtrmapbt_commit_staged_btree`
- Geometry:
  - `xfs_rtrmapbt_maxrecs`
  - `xfs_rtrmapbt_compute_maxlevels`
  - `xfs_rtrmapbt_droot_maxrecs`
  - `xfs_rtrmapbt_maxlevels_ondisk`
- Cache lifecycle:
  - `xfs_rtrmapbt_init_cur_cache`
  - `xfs_rtrmapbt_destroy_cur_cache`
- Reservation sizing:
  - `xfs_rtrmapbt_calc_reserves`
  - `xfs_rtrmapbt_calc_size`
- Format conversion:
  - `xfs_iformat_rtrmap`
  - `xfs_rtrmapbt_to_disk`
  - `xfs_iflush_rtrmap`
- Creation and special setup:
  - `xfs_rtrmapbt_create`
  - `xfs_rtrmapbt_init_rtsb`
  - `xfs_rtrmap_highest_rgbno`

## Layout Helpers

Provides address helpers for:
- incore records
- incore low keys
- incore high keys
- incore pointers
- on-disk root records
- on-disk root keys
- on-disk root pointers

Because the rmap btree is overlapping, internal nodes reserve space for two keys per pointer.

## Important Invariants

- `XFS_RTRMAP_BLOCK_LEN` uses CRC long btree block header size.
- Leaf roots store `struct xfs_rmap_rec`.
- Internal roots store two `struct xfs_rmap_key` values plus one pointer per record.
- On-disk and incore root sizes differ and must be calculated with the provided helpers.

## Research Notes

This header exposes layout details used by both kernel and userspace tools. Consumers should use its helpers instead of open-coding offsets.
