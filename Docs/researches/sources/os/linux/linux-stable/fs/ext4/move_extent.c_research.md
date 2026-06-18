# File Research: sources/os/linux/linux-stable/fs/ext4/move_extent.c

## Summary
Implements ext4 online extent movement used by defragmentation. It exchanges mapped extents between an original file and a donor file, optionally preserves original data through the page cache, and handles validation, journaling, retry, and partial-failure repair.

## Main Responsibilities
- Validate whether two inodes can participate in extent movement.
- Adjust requested logical-block ranges against alignment, file size, and ext4 extent limits.
- Lock both inodes and relevant folios in stable order to avoid deadlocks.
- Recheck extent-status sequence state after folio locking to detect stale mappings.
- Swap extents through `ext4_swap_extents()`.
- Copy original data back into the moved destination when donor/original written-state requires it.
- Mark fast commit ineligible for move-extent transactions.
- Retry on stale extent state, ENOSPC, and transient EBUSY/journal conditions.
- Discard preallocations after successful movement.

## Key Data Structures
- `struct mext_data`: carries original inode, donor inode, current original mapping, and donor logical block.
- `enum mext_move_type`: distinguishes skipped extents, metadata-only moves, and moves requiring data copy.
- `struct folio *folio[2]`: paired original/donor locked cache folios covering the active move window.
- `struct ext4_map_blocks`: used for both original and donor logical-to-physical extent state.

## Key Functions
- `ext4_double_down_write_data_sem()` / `ext4_double_up_write_data_sem()`: lock and unlock two ext4 inode `i_data_sem` semaphores in inode-address order with nested lock annotation.
- `mext_folio_double_lock()`: obtains both source and donor folios with NOFS allocation behavior, waits for writeback, and returns folios in caller inode order.
- `mext_folio_mkuptodate()`: ensures relevant buffers in a locked folio are uptodate, mapping missing buffers with `ext4_get_block()` and issuing synchronous buffer reads.
- `mext_move_begin()`: locks folios, validates the original extent-status sequence, bounds movement to folio and donor mapping lengths, and chooses skip/move/copy behavior.
- `mext_folio_mkwrite()`: rebuilds buffer mappings for the original inode after the swap and commits the moved range in the folio.
- `mext_move_extent()`: journaled core operation; starts a move-extent transaction, swaps extents, copies data if needed, records the write in jbd2, and attempts reverse repair on copy failure.
- `mext_check_validity()`: rejects unsupported cases: same inode, different filesystem, non-regular files, bigalloc, DAX, full data journaling, encrypted files, non-extent files, donor suid/sgid/immutable/append, swapfiles, quota files, and zero-size files.
- `mext_check_adjust_range()`: enforces matching page-relative start offsets, EXT_MAX_BLOCKS bounds, and EOF truncation.
- `ext4_move_extents()`: exported entry point coordinating inode locking, DIO draining, per-extent mapping, retry loops, and moved-length accounting.

## Synchronization and Lifetime
- Uses `lock_two_nondirectories()` to protect both inodes against truncate.
- Waits for direct I/O on both inodes before changing extents.
- Uses inode-address-ordered folio locking and `i_data_sem` double locking to avoid deadlock.
- Uses folio writeback waits before manipulating mappings.
- Uses `i_es_seq` to detect mapping invalidation while `i_data_sem` was not held.
- Wraps metadata changes in `EXT4_HT_MOVE_EXTENTS` transactions.
- Uses `filemap_release_folio()` to detach existing buffer state before extent swapping.

## Dependencies
Depends on ext4 extent mapping/swap code, jbd2 journaling, page-cache folios, buffer heads, ext4 quota checks, fast-commit exclusion, tracepoints, and retry helpers.

## Risks and Edge Cases
- Data preservation depends on successful folio read and post-swap `mkwrite`; the repair path swaps extents back but logs an inode/block error if repair is incomplete.
- The operation is intentionally unsupported for bigalloc, DAX, encryption, non-extent files, and data journaling because extent exchange semantics would be unsafe or undefined there.
- Stale extent-status detection is necessary because mappings can change while folios are being acquired.
- A short successful `ext4_swap_extents()` is treated as an I/O error because the caller expects all-or-nothing movement for the active extent segment.
