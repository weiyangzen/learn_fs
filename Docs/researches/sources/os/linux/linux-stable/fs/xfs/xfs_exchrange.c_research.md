# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_exchrange.c

## Purpose

Implements XFS file range exchange and commit-range ioctls. This is the user-facing orchestration layer that validates two file/range requests, flushes and locks affected state, reserves quota, calls the lower exchange-mapping engine, and handles commit freshness tokens.

## Main Responsibilities

- Provides inode locking helpers for exchange-map operations:
  - `xfs_exchrange_ilock`
  - `xfs_exchrange_iunlock`
  - `xfs_exchrange_estimate`
- Validates exchange requests:
  - same mount
  - regular files only
  - read/write access on both files
  - no append-only descriptors
  - immutable and swapfile rejection
  - non-overlap for same-inode exchanges
  - offset, length, EOF, and file-size-limit checks
- Handles allocation-unit alignment:
  - regular block-size alignment
  - realtime extent alignment, including non-power-of-two realtime extents
  - partial EOF block/extent restrictions
- Prepares files by waiting for direct I/O, writing dirty cache, flushing/unmapping ranges, attaching dquots, and canceling speculative CoW preallocations.
- Executes mapping exchange through `xfs_exchange_mappings`.
- Reserves quota for net and gross mapped block changes, including retry after blockgc quota cleanup.
- Implements ioctls:
  - `xfs_ioc_exchange_range`
  - `xfs_ioc_start_commit`
  - `xfs_ioc_commit_range`

## Key Data Flow

Userspace exchange arguments are copied into `struct xfs_exchrange`, then passed through `xfs_exchange_range`. The flow is:

1. Generic VFS-facing validation.
2. IO/MMAP lock acquisition.
3. XFS-specific preparation and freshness checks.
4. Transaction allocation and inode join.
5. Quota reservation.
6. Dry-run exit or mapping exchange.
7. timestamp updates, sync transaction handling, and optional in-core size swap for EOF exchanges.
8. privilege stripping and fsnotify modify events.

## Important Invariants

- Both files must be on the same mount and both realtime or both non-realtime.
- Exchange range offsets must align to the file allocation unit.
- A partial EOF allocation unit can only move to another EOF-compatible location.
- Freshness checks compare inode number, generation, ctime, and mtime under inode metadata locks.
- `XFS_EXCHANGE_RANGE_TO_EOF` may exchange unequal file sizes and swaps in-core sizes after committed mapping updates.
- Private internal flags occupy high bits and are filtered from userspace.

## Dependencies

- Uses `xfs_exchmaps` for the actual mapping exchange and reservation estimate.
- Uses reflink helpers to cancel CoW fork preallocations.
- Uses quota transaction helpers for dquot accounting.
- Uses VFS helpers for `remap_verify_area`, direct I/O waits, pagecache writeback, privilege removal, and fsnotify.

## Research Notes

This file is the policy and correctness wrapper around lower-level map swapping. The most sensitive parts are alignment/EOF validation, freshness-token handling for commit-range, quota retry behavior, and the exact ordering of IO locks, metadata locks, transaction joins, and pagecache flushing.
