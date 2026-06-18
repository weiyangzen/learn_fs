# File Research: sources/os/linux/linux-stable/fs/btrfs/discard.c

## Purpose
Implements Btrfs asynchronous discard for data-only block groups. It queues free-space trim work outside transaction commit, prioritizes recently freed large extents before bitmap-backed ranges, rate-limits discard IO, and handles fully free block groups before they enter the normal unused block group deletion path.

## Main State And Policy
- Uses `fs_info->discard_ctl` as the controller: delayed work, ordered discard workqueue, per-list queues, current running block group, byte/IOPS limits, previous discard timing, and aggregate discardable counters.
- Maintains `BTRFS_NR_DISCARD_LISTS` queues. Index `BTRFS_DISCARD_INDEX_UNUSED` is special for empty block groups; normal lists use decreasing minimum-size filters: no filter, `BTRFS_ASYNC_DISCARD_MAX_FILTER`, and `BTRFS_ASYNC_DISCARD_MIN_FILTER`.
- Only queues data-only block groups. Mixed block groups are explicitly excluded.
- Treats an empty remapped block group differently: `BTRFS_BLOCK_GROUP_REMAPPED` uses `identity_remap_count == 0`; otherwise emptiness means `used == 0 && remap_bytes == 0`.

## Key Flows
- `btrfs_discard_queue_work()` is the external enqueue path. It checks `DISCARD_ASYNC`, sends empty groups to `add_to_discard_unused_list()`, non-empty groups to `add_to_discard_list()`, and schedules delayed work if needed.
- `btrfs_discard_workfn()` is the worker. It picks an eligible block group with `peek_discard_list()`, verifies discard is still enabled and due, runs one trim segment, updates pass state, stores `prev_discard` and `prev_discard_time`, drops its temporary reference, and schedules the next run.
- `peek_discard_list()` selects work, repairs state transitions for block groups that changed while queued, initializes the cursor on `BTRFS_DISCARD_RESET_CURSOR`, and records a stable `discard_state`/`discard_index` snapshot for the current worker pass.
- The worker does two normal passes: `BTRFS_DISCARD_EXTENTS` via `btrfs_trim_block_group_extents()`, then `BTRFS_DISCARD_BITMAPS` via `btrfs_trim_block_group_bitmaps()`. A fully remapped empty block group uses `btrfs_trim_fully_remapped_block_group()`.
- `btrfs_finish_discard_pass()` removes a completed block group from discard queues, marks fully trimmed empty groups unused via `btrfs_mark_bg_unused()`, requeues untrimmed empty groups on the unused discard list, or advances non-empty groups through the filter lists.
- `btrfs_discard_punt_unused_bgs_list()` moves existing `fs_info->unused_bgs` entries into the async discard path when async discard is enabled, preserving reference ownership.
- `btrfs_discard_resume()`, `btrfs_discard_stop()`, `btrfs_discard_init()`, and `btrfs_discard_cleanup()` provide lifecycle integration for mount/remount/unmount.

## Scheduling And Rate Limiting
- `btrfs_discard_schedule_work()` wraps `__btrfs_discard_schedule_work()` under `discard_ctl->lock`.
- Scheduling delay is the max of the base `delay_ms`, byte-rate delay derived from `kbps_limit` and `prev_discard`, and block-group `discard_eligible_time`.
- `override` lets transaction-commit recalculation adjust the timer while accounting for elapsed time since the previous discard.
- `btrfs_discard_calc_delay()` derives `delay_ms` from `iops_limit`, clamped between 0/1 ms and 1000 ms. It also corrects negative aggregate discardable counters defensively.

## Counters And Accounting
- `btrfs_discard_update_discardable()` propagates per-block-group free-space-cache discardable extent/byte deltas into global atomic counters. It requires the free-space controller tree lock.
- Worker counters distinguish extent-pass bytes (`discard_extent_bytes`) from bitmap-pass bytes (`discard_bitmap_bytes`).
- `discard_bytes_saved` is initialized here but updated elsewhere.

## Concurrency And Lifetime
- Queue membership and `discard_ctl->block_group` are protected by `discard_ctl->lock`.
- Queued block groups hold references via `btrfs_get_block_group()` and release them on removal/purge.
- `btrfs_discard_cancel_work()` removes a block group and, if it was the active one, synchronously cancels the delayed work before rescheduling.
- `btrfs_discard_cleanup()` stops discard, cancels pending delayed work synchronously, and purges all discard lists.
- `btrfs_discard_purge_list()` deliberately drops `discard_ctl->lock` while calling `btrfs_mark_bg_unused()` to avoid doing heavier work under the spinlock.

## Important Dependencies
- Free-space trimming and state: `btrfs_trim_block_group_extents()`, `btrfs_trim_block_group_bitmaps()`, `btrfs_is_free_space_trimmed()`.
- Block group lifecycle: `btrfs_mark_bg_unused()`, `btrfs_get_block_group()`, `btrfs_put_block_group()`.
- Mount/unmount integration: `disk-io.c` initializes discard state, creates/destroys the discard workqueue, resumes discard after writable mount setup, and calls cleanup during close.
