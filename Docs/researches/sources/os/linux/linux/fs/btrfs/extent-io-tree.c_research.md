# File Research: sources/os/linux/linux/fs/btrfs/extent-io-tree.c

## Purpose

`extent-io-tree.c` implements Btrfs byte-range state tracking using an RB-tree of `extent_state` records. It supports setting, clearing, converting, locking, waiting on, querying, counting, and iterating state bits over inclusive byte ranges.

This state engine underpins inode I/O state, delalloc tracking, dirty metadata tracking, pinned extents, log ranges, excluded extents, device allocation state, and selftests.

## Core Data Model

- `struct extent_io_tree` owns an RB-tree of `extent_state` records and a spinlock.
- `struct extent_state` records:
  - inclusive `start` and `end`
  - RB-tree node
  - waitqueue
  - refcount
  - bitmask state
  - optional debug leak-list node

Ranges are split when operations affect only part of a state and merged when adjacent states have identical mergeable bits.

## Allocation and Debugging

- `alloc_extent_state()` allocates from the `btrfs_extent_state` slab cache.
- `btrfs_free_extent_state()` drops refcounts and frees only at zero refs.
- Debug builds track all allocated states and report leaks.
- Debug range checks detect suspicious inode I/O ranges.

Slab lifecycle:

- `btrfs_extent_state_init_cachep()`
- `btrfs_extent_state_free_cachep()`

## Tree Initialization and Release

- `btrfs_extent_io_tree_init()` initializes the RB-tree, spinlock, owner, and owner pointer.
- `btrfs_extent_io_tree_release()` removes all states from a tree, asserting no lock bits and no waiters remain.

## Search Helpers

The file provides internal search helpers:

- `tree_search_for_insert()`: finds containing or next state and optional insertion parent/link.
- `tree_search_prev_next()`: finds containing state or neighboring previous/next states.
- `tree_search()`: inexact search returning containing or next state.
- `find_first_extent_bit_state()`: finds first state with any requested bit.

## Set/Clear/Convert Mechanics

`set_extent_bit()` is the central set operation. It:

- handles `EXTENT_NOWAIT` by selecting `GFP_NOWAIT`
- preallocates state records
- detects exclusive lock-bit conflicts
- splits existing ranges as needed
- inserts state records into holes
- sets requested bits
- caches useful states for repeated calls
- merges adjacent compatible states

Public wrappers include:

- `btrfs_set_extent_bit()`
- `btrfs_set_record_extent_bits()`

`btrfs_clear_extent_bit_changeset()` is the central clear operation. It:

- optionally treats `EXTENT_CLEAR_ALL_BITS` as deletion
- handles delalloc/noreserve coupling
- splits states around the cleared range
- clears requested bits
- wakes waiters for lock-bit clears
- deletes empty states
- records changesets when requested

Public wrappers include:

- `btrfs_clear_extent_bit()`
- `btrfs_clear_record_extent_bits()`
- `btrfs_unlock_extent()`
- `btrfs_unlock_dio_extent()`

`btrfs_convert_extent_bit()` converts one set of bits to another over a range, intended for mergeable state transitions such as delalloc-to-dirty, not boundary/lock semantics.

## Locking and Waiting

- `btrfs_try_lock_extent_bits()` tries to set exclusive lock bits and rolls back partial success on conflict.
- `btrfs_lock_extent_bits()` retries on `-EEXIST`, waits on conflicting states via `wait_extent_bit()`, then tries again.
- `wait_extent_bit()` waits uninterruptibly on state waitqueues until requested lock bits clear.
- `state_wake_up()` wakes waiters when `EXTENT_LOCK_BITS` are cleared.

## Query Helpers

- `btrfs_find_first_extent_bit()`: finds first state with any requested bit.
- `btrfs_find_contiguous_extent_bit()`: returns the full contiguous span with requested bits.
- `btrfs_find_delalloc_range()`: finds a delalloc run up to `max_bytes`, respecting boundaries.
- `btrfs_find_first_clear_extent_bit()`: finds the first range where requested bits are not set, treating holes as clear.
- `btrfs_count_range_bits()`: counts bytes with all requested bits set, optionally requiring contiguity.
- `btrfs_test_range_bit_exists()`: checks whether a bit exists anywhere in a range.
- `btrfs_test_range_bit()`: checks whether a whole half-open range contains one bit continuously.
- `btrfs_get_range_bits()`: ORs all state bits present over a range and caches the first found state.
- `btrfs_next_extent_state()`: returns a referenced next state for controlled iteration.

## Changeset Accounting

`add_extent_changeset()` records changed byte counts and optionally changed ranges in an `extent_changeset`. Set/clear record wrappers use this to report what actually changed.

## Integration Points

For inode-owned trees, bit changes call delalloc accounting hooks:

- `btrfs_set_delalloc_extent()`
- `btrfs_clear_delalloc_extent()`
- `btrfs_merge_delalloc_extent()`
- `btrfs_split_delalloc_extent()`

The file also emits Btrfs tracepoints for allocation, free, set, clear, and convert operations.

## Risks and Invariants

- All tree mutations require `tree->lock`.
- States with lock bits or boundary bits are not merged.
- Refcounted cached states must be freed by callers or replaced safely.
- Waitqueue activity is protected by the tree lock; release asserts there are no waiters.
- Inclusive end offsets are used internally; some public comments explicitly distinguish half-open caller semantics.
- Allocation retries deliberately drop the spinlock and reschedule when needed.
