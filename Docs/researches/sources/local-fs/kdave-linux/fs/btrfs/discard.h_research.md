# File Research: sources/local-fs/kdave-linux/fs/btrfs/discard.h

## Role

Declares the internal Btrfs async-discard interface and the discard filter size constants used by `discard.c` and related free-space/block-group code.

## Key Definitions

- `BTRFS_ASYNC_DISCARD_DEFAULT_MAX_SIZE`: default maximum async discard size, 64 MiB.
- `BTRFS_ASYNC_DISCARD_MAX_FILTER`: large extent filter threshold, 1 MiB.
- `BTRFS_ASYNC_DISCARD_MIN_FILTER`: small extent filter threshold, 32 KiB.
- Forward declarations cover `btrfs_fs_info`, `btrfs_discard_ctl`, and `btrfs_block_group`.

## API Surface

- Queue/list operations: `btrfs_discard_check_filter()`.
- Work operations: `btrfs_discard_cancel_work()`, `btrfs_discard_queue_work()`, `btrfs_discard_schedule_work()`.
- Accounting operations: `btrfs_discard_calc_delay()`, `btrfs_discard_update_discardable()`.
- Setup and lifecycle: `btrfs_discard_punt_unused_bgs_list()`, `btrfs_discard_resume()`, `btrfs_discard_stop()`, `btrfs_discard_init()`, `btrfs_discard_cleanup()`.

## Dependencies

Includes Linux integer and size definitions only. The header intentionally keeps consumers decoupled from the discard controller and block-group structure definitions.

## Research Notes

This is a narrow subsystem header. It exposes enough for mount/unmount, transaction commit, free-space accounting, and block-group lifecycle code to drive async discard while keeping the queueing and worker state machine private to `discard.c`.
