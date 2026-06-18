# File Research: sources/local-fs/kdave-linux/fs/btrfs/discard.c

## Role

Implements Btrfs asynchronous discard for data-only block groups. It schedules and rate-limits trim work outside transaction commit, tracks block groups on multiple discard queues, advances each block group through extent and bitmap trimming passes, and hands completely free and fully trimmed block groups back to the unused-block-group path.

## Core Model

- `BTRFS_DISCARD_DELAY` gives recently freed space a 120-second reuse window before ordinary async discard work starts.
- `BTRFS_DISCARD_UNUSED_DELAY` gives fully free block groups a shorter 10-second delay before final discard and unused block group processing.
- `discard_minlen[]` defines the three queue filters: unused/full-free queue, large extent filter (`BTRFS_ASYNC_DISCARD_MAX_FILTER`), and smaller extent filter (`BTRFS_ASYNC_DISCARD_MIN_FILTER`).
- `discard_ctl->discard_list[]` stores block groups by discard priority/pass. Each queued block group has a `discard_index`, `discard_state`, `discard_cursor`, and `discard_eligible_time`.
- The code supports data-only block groups and explicitly avoids mixed block groups.
- Empty block-group detection uses `used == 0 && remap_bytes == 0`, or `identity_remap_count == 0` for remapped block groups.

## Queue Management

- `btrfs_run_discard_work()` gates async discard on a writable superblock and `BTRFS_FS_DISCARD_RUNNING`.
- `__add_to_discard_list()` initializes a block group's discard cursor state, eligibility time, and reference, then moves it to the tail of the selected discard list.
- `add_to_discard_list()` filters out non-data-only groups and disabled discard state before queueing.
- `add_to_discard_unused_list()` moves fully empty groups to `BTRFS_DISCARD_INDEX_UNUSED`, using the shorter unused delay and taking a reference if the group was not already queued.
- `remove_from_discard_list()` removes a queued or currently running block group, drops queue references, clears eligibility time, and tells the caller whether it removed the active work item.
- `find_next_block_group()` scans all discard lists for the earliest eligible block group, preferring an already-eligible group when found.
- `peek_discard_list()` chooses a block group for the worker, handles stale unused-list entries that are no longer empty, initializes the state machine, and records the active block group under `discard_ctl->block_group`.

## Worker State Machine

`btrfs_discard_workfn()` performs at most one trim step per work invocation:

- It gets the next eligible block group through `peek_discard_list()`.
- It exits or reschedules if discard has stopped or the selected group is not eligible yet.
- For `BTRFS_DISCARD_EXTENTS`, it calls `btrfs_trim_block_group_extents()` and accumulates `discard_extent_bytes`.
- For `BTRFS_DISCARD_BITMAPS`, it calls `btrfs_trim_block_group_bitmaps()` with the current minimum length and a previous-list maximum length filter, then accumulates `discard_bitmap_bytes`.
- For `BTRFS_DISCARD_FULLY_REMAPPED`, it calls `btrfs_trim_fully_remapped_block_group()`.
- When the block-group cursor reaches the end of the group, the worker either switches from extent pass to bitmap pass or calls `btrfs_finish_discard_pass()`.
- It records `prev_discard` and `prev_discard_time` for rate-limit scheduling before releasing the active block group and scheduling the next work item.

## Scheduling and Rate Limits

- `btrfs_discard_schedule_work()` wraps `__btrfs_discard_schedule_work()` with the discard lock.
- `__btrfs_discard_schedule_work()` respects pending delayed work unless `override` is set, starts from `discard_ctl->delay_ms`, and increases delay to account for:
  - `kbps_limit` derived from the size of the previous discard;
  - block-group eligibility time;
  - elapsed time since the previous discard when overriding an existing timer.
- `btrfs_discard_calc_delay()` derives the base delay from `iops_limit`, clamps it between 0/1 ms and 1000 ms, and defensively corrects negative discardable extent/byte counters.

## Public Operations

- `btrfs_discard_check_filter()` reprioritizes a block group if a newly freed/coalesced range is large enough for an earlier discard filter list.
- `btrfs_discard_cancel_work()` removes a block group and, if it was active, cancels the delayed worker synchronously and reschedules.
- `btrfs_discard_queue_work()` queues a block group on the unused or ordinary discard path and starts the delayed work if needed.
- `btrfs_discard_update_discardable()` propagates per-block-group free-space-cache discardable extent/byte deltas to the global discard controller.
- `btrfs_discard_punt_unused_bgs_list()` moves already marked unused block groups back through async discard when async discard is enabled.
- `btrfs_discard_resume()`, `btrfs_discard_stop()`, `btrfs_discard_init()`, and `btrfs_discard_cleanup()` manage lifecycle and cleanup.

## Concurrency and Lifetime

- `discard_ctl->lock` protects discard queues, active block group pointer, scheduling state, and state transitions.
- Queued block groups hold an extra block-group reference until removed or purged.
- Active worker state holds an additional reference while trimming.
- Cleanup stops discard, cancels the delayed worker, then purges all lists. Purging marks fully free block groups unused when async discard is being disabled.
- The code carefully avoids an infinite loop in `peek_discard_list()` if a group on the unused list is no longer empty and discard was disabled or the group is no longer data-only.

## Dependencies

Uses Btrfs block-group, free-space-cache, filesystem option, unused block-group, and trim helpers. It is invoked by block-group/free-space code when free space changes, by transaction/commit paths for discardable accounting and delay recalculation, and by mount/unmount paths through discard init/resume/cleanup.

## Research Notes

The file's central design is to convert discard from a synchronous transaction-commit cost into a controlled delayed background process. The in-memory free-space cache is the source of discard state, so state is intentionally rebuilt as untrimmed after mount or crash. The implementation accepts some overtrimming, especially for bitmap-backed free space, to get better coalescing and cheaper accounting.
