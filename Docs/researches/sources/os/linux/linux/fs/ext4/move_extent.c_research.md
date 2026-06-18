# File Research: sources/os/linux/linux/fs/ext4/move_extent.c

## Purpose
Implements ext4 online extent movement/exchange for defragmentation via `ext4_move_extents()`. It coordinates two regular extent-based files: an original file whose extents are improved and a donor file that supplies replacement extents.

## Main Entry Points
- `ext4_move_extents()` validates the two files, locks both inodes against truncate, waits for direct I/O, bounds the requested logical block ranges, maps source extents, and repeatedly moves/copies ranges.
- `ext4_double_down_write_data_sem()` / `ext4_double_up_write_data_sem()` provide ordered locking for two inode extent trees.
- `mext_move_extent()` performs one journaled extent swap and optional data copy.

## Control Flow
The implementation first rejects unsupported cases: same inode, different filesystem, non-regular files, bigalloc, DAX, data journaling, encryption, non-extent files, unsuitable donor flags, swap files, quota files, and zero-sized files. Range validation enforces matching page-offset alignment, `EXT_MAX_BLOCKS` bounds, and EOF trimming.

For each mapped source range, `mext_move_extent()` starts a move-extents journal transaction, marks fast commit ineligible, locks corresponding folios from both files in stable inode order, rechecks the original extent-status sequence, maps the donor range, and classifies the operation as skip, pure extent move, or data-copy move. It releases page-cache buffer mappings, swaps extents under both `i_data_sem` locks with `ext4_swap_extents()`, and for data-copy cases rebuilds original file buffers, commits dirty page-cache data, and records the write in the journal. If data copying fails after a swap, it attempts to swap the extents back and reports potential data loss on unrecoverable repair failure.

## Integration Points
Depends on ext4 extent mapping and swapping (`ext4_map_blocks()`, `ext4_swap_extents()`), journaling (`ext4_journal_start()`, `ext4_jbd2_inode_add_write()`), folio/page-cache buffer helpers, direct-I/O synchronization, preallocation discard, tracepoints, and fast-commit exclusion.

## Invariants and Risks
Deadlock avoidance is central: inode semaphores and folio locks are acquired in stable inode order. The extent-status sequence check guards against stale mappings observed before folio locking. The repair path is safety-critical because extent swap succeeds before data recopy can fail. Unsupported modes are deliberately rejected rather than approximated.

## Testing Signals
Exercise successful pure unwritten swaps, data-copy swaps, holes/delalloc skip paths, EOF-shortened moves, `-ESTALE` retry, ENOSPC retry, EBUSY journal-force retry, and copy-failure repair behavior.
