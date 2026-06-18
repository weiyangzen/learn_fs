# File Research: sources/os/linux/linux/fs/xfs/xfs_extent_busy.c

Tracks freed extents that are still “busy” because their freeing transactions have not committed or discard is still in flight. Each group has a spinlock-protected rb-tree keyed by block number plus transaction/discard lists.

Key logic:
- `xfs_extent_busy_insert_list`, `xfs_extent_busy_insert`, and `xfs_extent_busy_insert_discard` allocate busy records, hold the group, insert non-overlapping ranges into the rb-tree, and append them to the caller’s list.
- `xfs_extent_busy_search` reports no overlap, exact overlap, or partial overlap for allocation decisions.
- `xfs_extent_busy_update_extent` lets allocator reuse safe portions of non-userdata busy extents by trimming/removing records; otherwise it forces the log and retries. It cannot split an immutable transaction/CIL busy-list record.
- `xfs_extent_busy_reuse` walks overlapping busy extents and applies safe reuse updates.
- `xfs_extent_busy_trim` trims allocation candidates away from busy ranges, records the busy generation for waiters, and prefers forward allocation patterns to reduce fragmentation.
- `xfs_extent_busy_clear` removes busy entries after commit, optionally marking them as undergoing discard instead of immediately unbusy, increments generation, and wakes waiters.
- `xfs_extent_busy_flush` forces the log and waits for generation changes while avoiding deadlocks with busy extents held by the current transaction.
- `xfs_extent_busy_wait_all` drains all AG and eligible realtime-group busy trees.
- `xfs_extent_busy_ag_cmp`, `xfs_extent_busy_list_empty`, and `xfs_extent_busy_alloc` provide sorting, state query, and tree allocation support.

The concurrency model hinges on `eb_lock`, `eb_gen`, and `eb_wait`: allocators can trim or wait on a generation, while commit/discard completion wakes them after clearing records.
