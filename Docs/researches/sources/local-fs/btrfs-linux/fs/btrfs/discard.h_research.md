# File Research: sources/local-fs/btrfs-linux/fs/btrfs/discard.h

## Summary
Declares the Btrfs async discard interface and discard filter size constants.

## Main Contents
- Default max discard size: `BTRFS_ASYNC_DISCARD_DEFAULT_MAX_SIZE` at 64 MiB.
- High-size filter: `BTRFS_ASYNC_DISCARD_MAX_FILTER` at 1 MiB.
- Low-size filter: `BTRFS_ASYNC_DISCARD_MIN_FILTER` at 32 KiB.
- Public discard queue, schedule, accounting, lifecycle, and resume/stop function declarations.

## Key Interfaces
The header exposes queueing and cancellation (`btrfs_discard_queue_work()`, `btrfs_discard_cancel_work()`), scheduling (`btrfs_discard_schedule_work()`), accounting (`btrfs_discard_calc_delay()`, `btrfs_discard_update_discardable()`), and lifecycle operations (`btrfs_discard_init()`, `btrfs_discard_resume()`, `btrfs_discard_stop()`, `btrfs_discard_cleanup()`).

## Important Details
The header only forward-declares `btrfs_fs_info`, `btrfs_discard_ctl`, and `btrfs_block_group`, keeping discard internals private to implementation files and shared Btrfs structs.

## Risks
Callers must only use these helpers when async discard mount options and block-group type checks make sense. The implementation further rejects non-data-only or disabled-discard cases, but incorrect callers can still cause unnecessary scheduling attempts.
