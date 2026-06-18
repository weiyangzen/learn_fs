# File Research: sources/os/linux/linux/block/badblocks.c

`badblocks.c` implements generic bad-sector range tracking for block devices. It is based on MD badblocks code and stores bad ranges in a compact, sorted table of 64-bit entries: offset, length, and acknowledged state.

Core model:
- Ranges are tracked in sectors, optionally shifted to represent larger units.
- Entries can be acknowledged or unacknowledged.
- `MAX_BADBLOCKS` limits table capacity; each entry length is capped by `BB_MAX_LEN`.
- A seqlock protects readers and writers; readers retry on concurrent writes.
- The table is kept ordered and opportunistically merged to conserve entries.

Set path:
- `_badblocks_set()` handles all range insertion logic under `write_seqlock_irqsave`.
- It rounds start/end according to `bb->shift`, rejects disabled or zero-length input, and processes large ranges piece by piece.
- Helpers include `prev_badblocks()`, `prev_by_hint()`, `can_merge_front()`, `front_merge()`, `can_combine_front()`, `front_combine()`, `overlap_front()`, `overlap_behind()`, `can_front_overwrite()`, `front_overwrite()`, `insert_at()`, and `try_adjacent_combine()`.
- The algorithm handles non-overlap, overlap, acknowledged-over-unacknowledged overwrite, adjacent merges, full-table pressure, and post-overwrite front/behind combines.
- `badblocks_set()` exports this behavior and returns false for failure or partial failure.

Clear path:
- `_badblocks_clear()` removes or shrinks bad ranges under `write_seqlock_irq`.
- Clearing rounds conservatively: start up, end down, so blocks are not falsely marked good.
- `front_clear()` shrinks or deletes a range.
- `front_splitting_clear()` splits one range into two if clearing a middle segment and there is room.
- Clearing non-bad areas is treated as success; if a full table prevents a required split, the request is effectively dropped and can report failure.

Check path:
- `_badblocks_check()` searches for bad ranges intersecting a requested sector span.
- `badblocks_check()` wraps it in a seqlock read/retry loop.
- Return values: `0` no bad blocks, `1` only acknowledged bad blocks, `-1` at least one unacknowledged bad block.
- It reports the first overlapping bad range through `first_bad` and `bad_sectors`.

Acknowledgement and sysfs:
- `ack_all_badblocks()` marks all unacknowledged entries acknowledged only if `bb->changed` is clear, then merges adjacent compatible entries.
- `badblocks_show()` prints ranges, optionally only unacknowledged ranges, scaling offsets/lengths by `bb->shift`.
- `badblocks_store()` parses `"sector length"` and calls `badblocks_set()` with acknowledged state derived from the `unack` argument.

Lifetime:
- `badblocks_init()` and `devm_init_badblocks()` allocate the page-sized table and initialize the seqlock.
- `badblocks_exit()` frees the table, using device-managed or normal allocation depending on initialization mode.
- Exported symbols provide a reusable bad-range service for block/storage consumers.

Important behavior notes:
- Acknowledged state is ordered: acknowledged ranges may overwrite unacknowledged ranges, but unacknowledged ranges do not overwrite acknowledged ones.
- The implementation favors correctness over perfect compaction; rare unoptimized full-table cases may fail or leave merge opportunities unused.
- `bb->unacked_exist` is a cache that is recomputed when acknowledged ranges are updated or shown.
