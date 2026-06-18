# File Research: sources/local-fs/btrfs-linux/fs/btrfs/discard.c

## Summary
Implements Btrfs asynchronous discard/trim scheduling for data-only block groups. It keeps discard work outside transaction commit by maintaining per-filesystem discard queues, rate limits, eligibility delays, and block-group cursor state.

## Main Responsibilities
- Queue free or fully-free data block groups for async discard.
- Prioritize discard passes by block-group recency and free-space size filters.
- Run a delayed ordered work item that trims one region at a time.
- Track discardable byte/extent counters from free-space cache state.
- Move fully discarded empty block groups to the normal unused block-group path.
- Initialize, resume, stop, and clean up async discard state.

## Key APIs
- `btrfs_discard_queue_work()`
- `btrfs_discard_cancel_work()`
- `btrfs_discard_schedule_work()`
- `btrfs_discard_check_filter()`
- `btrfs_discard_calc_delay()`
- `btrfs_discard_update_discardable()`
- `btrfs_discard_punt_unused_bgs_list()`
- `btrfs_discard_resume()`
- `btrfs_discard_stop()`
- `btrfs_discard_init()`
- `btrfs_discard_cleanup()`

## Important Behavior
Async discard uses multiple lists in `btrfs_discard_ctl`. Index `BTRFS_DISCARD_INDEX_UNUSED` handles fully free block groups before they are released to `unused_bgs`; the other lists perform progressively smaller trim filters using `discard_minlen`.

Newly queued block groups get an eligibility timestamp. Normal discard waits about 120 seconds to favor reuse, while unused block groups wait about 10 seconds. `find_next_block_group()` chooses the earliest eligible group across all lists.

Discard work has a pass-based state machine:
- `BTRFS_DISCARD_RESET_CURSOR` initializes the cursor to the block-group start.
- `BTRFS_DISCARD_EXTENTS` trims free-space extent entries first.
- `BTRFS_DISCARD_BITMAPS` trims bitmap-backed free space afterward.
- `BTRFS_DISCARD_FULLY_REMAPPED` handles empty remapped block groups specially.

The delayed work delay is the maximum of the base IOPS delay, byte-rate delay from the previous trim, and the selected block group's eligibility timeout. `btrfs_discard_calc_delay()` recomputes the base delay from `iops_limit`, clamped between 0/1 ms and 1000 ms.

`btrfs_discard_update_discardable()` propagates block-group free-space-cache deltas to global async discard counters while the free-space tree lock is held.

## State and Synchronization
`discard_ctl->lock` protects discard lists, current running block group, eligibility time, previous discard timing, and scheduling decisions. Queued block groups hold a block-group reference until removed.

The work function temporarily stores the active block group in `discard_ctl->block_group` so cancellation can detect a currently running trim, cancel the delayed work synchronously, and reschedule.

## Risks
Discard state depends on free-space-cache bitmap semantics and is intentionally approximate. Trimmed bitmap state can be reset and retrimmed after later allocation/free patterns.

Reference ownership is subtle: list insertion takes a block-group reference, removal drops it, and unused block-group punting drops the reference previously held by `btrfs_mark_bg_unused()`.

`peek_discard_list()` must avoid loops when an unused-list block group is no longer empty. The code explicitly asserts that a data-only block group moved out of the unused index actually changed index.
