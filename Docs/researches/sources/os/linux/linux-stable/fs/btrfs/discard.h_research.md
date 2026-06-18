# File Research: sources/os/linux/linux-stable/fs/btrfs/discard.h

## Purpose
Declares the public async discard interface for Btrfs and defines discard size thresholds used by `discard.c`.

## Constants
- `BTRFS_ASYNC_DISCARD_DEFAULT_MAX_SIZE`: default max discard size, `64M`.
- `BTRFS_ASYNC_DISCARD_MAX_FILTER`: upper list filter, `1M`.
- `BTRFS_ASYNC_DISCARD_MIN_FILTER`: lower list filter, `32K`.

## Exported Operations
- Queue/list operations: `btrfs_discard_check_filter()`.
- Work operations: `btrfs_discard_cancel_work()`, `btrfs_discard_queue_work()`, `btrfs_discard_schedule_work()`.
- Counter/delay updates: `btrfs_discard_calc_delay()`, `btrfs_discard_update_discardable()`.
- Lifecycle: `btrfs_discard_punt_unused_bgs_list()`, `btrfs_discard_resume()`, `btrfs_discard_stop()`, `btrfs_discard_init()`, `btrfs_discard_cleanup()`.

## Dependencies
Forward-declares `btrfs_fs_info`, `btrfs_discard_ctl`, and `btrfs_block_group`; includes only Linux type/size headers. This keeps discard users from needing the full implementation unless they already require Btrfs internals.
