# File Research: sources/os/linux/linux/fs/xfs/xfs_zone_priv.h

## Purpose

Defines private data structures and helper declarations shared by XFS zoned allocator and GC implementation files.

## Main Responsibilities

- Defines `struct xfs_open_zone`.
- Defines `XFS_ZONE_USED_BUCKETS`.
- Defines `struct xfs_zone_info`.
- Declares open-zone, reset, GC, reclaimable, and reservation wake helpers.

## Important Invariants

- `oz_allocated` is protected by `oz_alloc_lock`.
- `oz_written` is protected by the rmap inode lock.
- `oz_rtg` remains constant for the open-zone lifetime.
- Open-zone list/counts are protected by `zi_open_zones_lock`.
- Reclaimable bucket bitmaps/counts are protected by `zi_used_buckets_lock`.
- Reservation waiters are protected by `zi_reservation_lock`.

## Dependencies

Used internally by `xfs_zone_alloc.c`, `xfs_zone_gc.c`, `xfs_zone_info.c`, and `xfs_zone_space_resv.c`.

## Research Notes

This header captures the private concurrency contract for zoned allocation.
