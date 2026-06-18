# File Research: sources/os/linux/linux/fs/xfs/xfs_zone_alloc.h

## Purpose

Declares the public zoned XFS allocation, reservation, I/O completion, and GC-control interfaces.

## Main Responsibilities

- Defines `struct xfs_zone_alloc_ctx`.
- Defines reservation flags: greedy, nowait, and reserved-pool use.
- Declares zoned space reserve/unreserve helpers.
- Declares zoned write allocation/submission and end-I/O mapping helpers.
- Declares zoned block free, wake, stats, mount, unmount, and GC control functions.
- Provides no-RT fallback stubs for mount/GC functions.

## Important Invariants

- Allocation contexts track both reserved blocks and a held open-zone reference.
- Zoned mount support requires `CONFIG_XFS_RT`.
- Reserved and nowait flags affect both user capacity and immediately available capacity accounting.

## Dependencies

Exposes interfaces used by XFS writeback, realtime allocation, free-space accounting, and mount code.

## Research Notes

This header is the main cross-file API for the zoned allocator stack.
