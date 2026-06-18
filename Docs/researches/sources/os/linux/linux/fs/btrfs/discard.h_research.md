# File Research: sources/os/linux/linux/fs/btrfs/discard.h

## Purpose

`discard.h` is the public interface for Btrfs asynchronous discard support.

## Exposed Constants

- `BTRFS_ASYNC_DISCARD_DEFAULT_MAX_SIZE`: default maximum async discard size, 64 MiB.
- `BTRFS_ASYNC_DISCARD_MAX_FILTER`: large discard filter, 1 MiB.
- `BTRFS_ASYNC_DISCARD_MIN_FILTER`: small discard filter, 32 KiB.

## Public API

List and queue management:

- `btrfs_discard_check_filter()`
- `btrfs_discard_cancel_work()`
- `btrfs_discard_queue_work()`
- `btrfs_discard_schedule_work()`

Accounting:

- `btrfs_discard_calc_delay()`
- `btrfs_discard_update_discardable()`

Lifecycle:

- `btrfs_discard_punt_unused_bgs_list()`
- `btrfs_discard_resume()`
- `btrfs_discard_stop()`
- `btrfs_discard_init()`
- `btrfs_discard_cleanup()`

## Integration Points

This header is consumed by mount/open/close code, free-space/block-group code, and transaction paths that need to queue, update, or shut down async discard.

## Invariants

The header only forward-declares Btrfs core structs, keeping the discard interface narrow and avoiding heavy include coupling.
