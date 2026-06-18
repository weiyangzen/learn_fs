# File Research: sources/os/linux/linux/fs/ocfs2/move_extents.c

`move_extents.c` implements the `OCFS2_IOC_MOVE_EXT` ioctl for explicit extent movement and automatic defragmentation. It copies data to new clusters, updates extent records, handles refcounted extents, frees old clusters through truncate log or refcount decrement, and returns partial progress to userspace.

Main responsibilities:
- Defines `struct ocfs2_move_extents_context`, carrying the target inode/file, mode flags, credits, new physical position, moved count, refcount location, user range, extent tree, metadata/data alloc contexts, and deferred deallocation context.
- `__ocfs2_move_extent()` performs the core move:
  - Copies cluster data page-by-page from old physical cpos to new physical cpos.
  - Locates the extent record for the logical cpos.
  - Verifies extent flags are unchanged.
  - Replaces/splits the extent with a new physical block, clearing `OCFS2_EXT_REFCOUNTED`.
  - Decreases refcount or appends old clusters to truncate log.
  - Updates inode fsync transaction state.
- Reserves metadata for split/move operations in `ocfs2_lock_meta_allocator_move_extents()`, including worst-case sparse extent expansion needs and journal credits.
- `ocfs2_defrag_extent()` allocates a fresh cluster run through normal allocation, optionally allows partial defrag, moves the extent in one transaction, frees newly allocated clusters on failure, and syncs COW/writeback data.
- Explicit move support:
  - Finds the allocation group containing a physical goal with `ocfs2_find_victim_alloc_group()`.
  - Aligns and validates the user-supplied goal with `ocfs2_validate_and_adjust_move_goal()`.
  - Probes a target group near the goal within a threshold using `ocfs2_probe_alloc_group()`.
  - `ocfs2_move_extent()` locks the global bitmap, claims the chosen target bits, updates bitmap counts, moves the extent, and syncs writeback.
- Defrag support:
  - `ocfs2_calc_extent_defrag_len()` accumulates small extents up to a threshold and skips already-large extents.
  - `__ocfs2_move_extents_range()` walks logical clusters with `ocfs2_get_clusters()`, skips holes, chooses defrag vs explicit move, invalidates stale extent cache after each successful move, tracks moved byte count/new offset, schedules truncate-log flush, and runs deferred deallocs.
- `ocfs2_move_extents()` enforces filesystem state and locking:
  - Rejects emergency readonly.
  - Takes inode mutex, OCFS2 rw lock, metadata lock, and `ip_alloc_sem`.
  - Runs the range move.
  - Updates inode ctime in a final inode-update transaction.
- `ocfs2_ioctl_move_extents()` validates userspace input:
  - Requires non-null arg, mount write access, regular writable file, and not immutable/append.
  - Clamps requested range to file size.
  - Defaults threshold to 1 MiB and caps it at file size.
  - Accepts only auto-defrag and partial-defrag flags.
  - Validates explicit move goals.
  - Copies result back even after partial/failing moves so userspace sees completed length and new offset.

Key invariants:
- Each moved extent is protected by journaling so metadata and old-cluster cleanup remain crash-consistent.
- Refcounted extents are unshared by the move path and require refcount-tree locking/preparation.
- Explicit movement cannot cross allocation group boundaries after goal validation.
- Extent cache is truncated after moving to prevent stale physical mapping or stale flags.
