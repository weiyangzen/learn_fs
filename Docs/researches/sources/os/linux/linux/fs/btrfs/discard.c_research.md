# File Research: sources/os/linux/linux/fs/btrfs/discard.c

## Purpose

`discard.c` implements Btrfs asynchronous discard, the background TRIM/discard engine for free regions in data-only block groups. It avoids doing large synchronous discards during transaction commit by queueing block groups on LRU-like discard lists and trimming one region at a time from delayed work.

The file explicitly excludes mixed block groups and relies on the in-memory free-space cache for discard state, so discard state is rebuilt after mount or crash rather than persisted.

## Main Concepts

- `btrfs_discard_ctl` is the central controller, owned by `btrfs_fs_info`.
- Block groups carry discard scheduling state: `discard_list`, `discard_index`, `discard_state`, `discard_cursor`, and `discard_eligible_time`.
- There are multiple discard lists indexed by priority/filter:
  - index 0: fully free/unused block groups waiting for final trim
  - later indexes: progressively smaller discard size filters
- The worker performs a two-pass trim:
  - `BTRFS_DISCARD_EXTENTS`: discard free-space extents first
  - `BTRFS_DISCARD_BITMAPS`: discard bitmap-backed free-space ranges later
  - `BTRFS_DISCARD_FULLY_REMAPPED`: special handling for remapped empty block groups

## Key Constants

- `BTRFS_DISCARD_DELAY`: initial 120 second delay before regular async discard.
- `BTRFS_DISCARD_UNUSED_DELAY`: shorter 10 second delay for unused block groups.
- `BTRFS_DISCARD_MAX_IOPS`: default 1000 IOPS cap.
- `discard_minlen[]`: discard size filters using `0`, `BTRFS_ASYNC_DISCARD_MAX_FILTER`, and `BTRFS_ASYNC_DISCARD_MIN_FILTER`.

## Important Functions

- `btrfs_discard_init()`: initializes lock, delayed work, list heads, counters, size limits, IOPS/KiB limits, and stats.
- `btrfs_discard_resume()`: enables async discard when the mount option is active and punts already-unused block groups into the discard pipeline.
- `btrfs_discard_stop()`: clears `BTRFS_FS_DISCARD_RUNNING`.
- `btrfs_discard_cleanup()`: stops discard, cancels delayed work, and purges queued block groups.
- `btrfs_discard_queue_work()`: queues a block group for async discard if `DISCARD_ASYNC` is enabled.
- `btrfs_discard_cancel_work()`: removes a block group and reschedules if the cancelled group was the active one.
- `btrfs_discard_schedule_work()`: computes delayed-work timing using IOPS, byte-rate, prior discard size, and block-group eligibility.
- `btrfs_discard_workfn()`: main state machine; selects a block group, trims one range, advances cursor/state, updates stats, and schedules the next unit.
- `btrfs_discard_check_filter()`: reprioritizes a block group when newly freed/coalesced space exceeds a higher filter.
- `btrfs_discard_update_discardable()`: propagates per-free-space-cache discardable byte/extent deltas to the global discard controller.
- `btrfs_discard_punt_unused_bgs_list()`: moves unused block groups into async discard before they go down the normal unused block-group path.

## Control Flow

1. A block group becomes discardable or unused.
2. `btrfs_discard_queue_work()` classifies it:
   - empty block groups go to the unused discard list
   - non-empty data-only block groups go to filtered discard lists
3. `btrfs_discard_schedule_work()` arms delayed work if needed.
4. `btrfs_discard_workfn()`:
   - selects an eligible block group with `peek_discard_list()`
   - initializes/reset cursor and state
   - trims extents, bitmaps, or fully remapped groups
   - moves the group to the next discard state/list or marks it unused
5. Cleanup/remount paths stop or purge the queues.

## Locking and Lifetime

- `discard_ctl->lock` protects discard lists, active `discard_ctl->block_group`, and scheduling state.
- Queued block groups receive an extra reference via `btrfs_get_block_group()`.
- Removal and purge paths drop the queue reference with `btrfs_put_block_group()`.
- `remove_from_discard_list()` also detects if the block group is currently active.

## Integration Points

- Uses block group helpers from `block-group.h`.
- Uses trim helpers from `free-space-cache.h`.
- Controlled by mount option `DISCARD_ASYNC`.
- Called from mount/resume, transaction/free-space accounting, unused block-group handling, and filesystem shutdown.
- `disk-io.c` calls `btrfs_discard_init()`, `btrfs_discard_resume()`, and `btrfs_discard_cleanup()`.

## Risks and Invariants

- Only data-only block groups are supported.
- Mixed block groups are intentionally skipped.
- The unused-list path must avoid infinite loops when an unused block group becomes non-empty before discard.
- Accurate block-group reference handling is critical because workqueue and queue ownership overlap.
- Delay calculation depends on corrected global discardable counters; negative counter drift is defensively repaired.
