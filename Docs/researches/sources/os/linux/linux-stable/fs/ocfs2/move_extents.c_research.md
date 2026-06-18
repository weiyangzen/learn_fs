# File Research: sources/os/linux/linux-stable/fs/ocfs2/move_extents.c

Purpose: implements the OCFS2 move-extents ioctl, supporting explicit physical-goal extent movement and automatic defragmentation by copying data to newly allocated clusters, updating extent records, handling refcounted extents, freeing old clusters, and reporting partial progress to userspace.

Read coverage: complete file read, 1,092 lines.

Key structures and state:
- `struct ocfs2_move_extents_context` carries inode/file, auto-defrag/partial flags, journal credits, latest new physical cluster, total moved clusters, refcount tree location, userspace range, dinode extent tree, metadata/data allocation contexts, and delayed deallocation context.
- Userspace `struct ocfs2_move_extents` supplies byte range, goal block, threshold, flags, and receives moved length/new offset/completion flag.

Major logic:
- `__ocfs2_move_extent()` copies data page-by-page from old clusters to new clusters, finds the target extent record, verifies flags, replaces/splits the extent record with the new physical location and refcount flag cleared, then frees old storage via refcount decrement or truncate-log append.
- `ocfs2_lock_meta_allocator_move_extents()` checks free extent record capacity, reserves extra metadata blocks when tree growth/sparse splits may need them, and adds extent-extension credits.
- `ocfs2_defrag_extent()` handles auto-defrag allocation: prepares refcount changes, reserves metadata and data clusters, flushes truncate log before cluster reservation to avoid global bitmap deadlock, supports partial defrag if requested, moves the extent, syncs writeback for copied data, and rolls back newly allocated clusters on selected failures.
- `ocfs2_find_victim_alloc_group()` raw-walks a system allocator's chain records and group descriptors to find the group containing a requested block.
- `ocfs2_validate_and_adjust_move_goal()` cluster-aligns explicit goals, validates that the goal is in the global bitmap, skips group descriptor block zero within a group, and rejects moves that would cross the group.
- `ocfs2_probe_alloc_group()` searches a victim group bitmap from the goal bit for a contiguous free run, allowing a bounded hop threshold.
- `ocfs2_move_extent()` handles explicit-goal movement: prepares refcount changes, reserves metadata, locks truncate log and global bitmap, probes/marks the target group, updates global bitmap inode/group counts, moves the extent, and syncs writeback.
- `ocfs2_calc_extent_defrag_len()` accumulates small extents until a threshold, skips already-large extents, or trims an extent to complete a threshold-sized defrag cycle.
- `__ocfs2_move_extents_range()` converts byte ranges to cluster ranges, skips empty/inline files and holes, iterates extents via `ocfs2_get_clusters()`, dispatches auto-defrag or explicit move, invalidates extent cache after each changed range, accumulates moved length/new offset, schedules truncate-log flush, and drains delayed deallocations.
- `ocfs2_move_extents()` serializes the operation with inode mutex, RW cluster lock, exclusive inode lock, and `ip_alloc_sem`, then updates inode ctime in a final transaction.
- `ocfs2_ioctl_move_extents()` validates userspace pointer, mount write access, regular writable file, immutable/append flags, range bounds, threshold/defaults, flags, explicit goal validity, executes the move, and copies progress back even after partial failure.

Important entry points:
- `ocfs2_ioctl_move_extents()`.
- Internal movement: `ocfs2_move_extents()`, `__ocfs2_move_extents_range()`, `ocfs2_defrag_extent()`, `ocfs2_move_extent()`, `__ocfs2_move_extent()`.

Concurrency and lifetime:
- Top-level movement holds inode mutex, OCFS2 RW lock, exclusive inode lock, and write side of `ip_alloc_sem`.
- Refcounted extents lock the refcount tree while preparing and applying refcount deletion.
- Truncate log inode mutex is used around truncate-log flush and old-cluster freeing decisions.
- Explicit-goal movement locks the global bitmap inode while marking target clusters allocated.
- Metadata/data allocation contexts and delayed deallocation contexts are freed/drained on exit.

Important dependencies:
- Uses OCFS2 extent tree mutation, cluster copy/COW writeback helpers, local alloc rollback, truncate log, global bitmap/suballocator updates, refcount tree, metadata allocator, inode locks, mount write accounting, and userspace copy helpers.

Risk and edge cases:
- Movement intentionally clears `OCFS2_EXT_REFCOUNTED` on replacement records because copied data is private after move.
- Partial defrag can reduce requested length; non-partial defrag clears completion and may return `-ENOSPC` after reporting progress.
- Explicit movement validates a goal before locking but global bitmap state can change later, so final probing/allocation can still fail.
- Truncate-log flush must occur before cluster reservation in defrag to avoid deadlock on the global bitmap.
- Range conversion ignores clusters containing unaligned start/end bytes for simplicity; movement is cluster-granular.
- Userspace receives `me_moved_len` and `me_new_offset` even when the operation fails after partial progress.
