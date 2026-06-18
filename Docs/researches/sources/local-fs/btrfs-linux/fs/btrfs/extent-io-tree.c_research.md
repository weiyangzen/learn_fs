# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent-io-tree.c

## Summary
Implements Btrfs extent state trees: rb-tree-backed interval state tracking for inode I/O, metadata dirty ranges, pinned extents, device allocation state, log ranges, and other filesystem-owned byte ranges.

## Main Responsibilities
- Allocate, reference, free, and leak-check `extent_state` records.
- Insert, split, merge, and remove byte-range state records.
- Set, clear, convert, test, count, and search extent-state bits.
- Provide blocking and nonblocking extent locks.
- Wake waiters when lock bits clear.
- Integrate inode I/O tree state changes with delalloc accounting callbacks.

## Key APIs
- Initialization/lifecycle: `btrfs_extent_io_tree_init()`, `btrfs_extent_io_tree_release()`, `btrfs_extent_state_init_cachep()`, `btrfs_extent_state_free_cachep()`.
- Locking: `btrfs_lock_extent_bits()`, `btrfs_try_lock_extent_bits()`.
- State mutation: `btrfs_set_extent_bit()`, `btrfs_set_record_extent_bits()`, `btrfs_clear_extent_bit_changeset()`, `btrfs_clear_record_extent_bits()`, `btrfs_convert_extent_bit()`.
- Search/query: `btrfs_find_first_extent_bit()`, `btrfs_find_first_clear_extent_bit()`, `btrfs_find_contiguous_extent_bit()`, `btrfs_find_delalloc_range()`, `btrfs_count_range_bits()`, `btrfs_test_range_bit()`, `btrfs_test_range_bit_exists()`, `btrfs_get_range_bits()`.
- Iteration: `btrfs_next_extent_state()`.

## Important Behavior
Each `extent_state` covers an inclusive byte range and a bitmask. Ranges are stored in an rb-tree and are split when a mutation touches only part of a record. Adjacent records with identical mergeable state are merged. Records with lock bits or `EXTENT_BOUNDARY` are not merged because waiters and I/O completion paths depend on stable records.

Set operations can take exclusive bits (`EXTENT_LOCKED` or `EXTENT_DIO_LOCKED`). If any part of the target range already has those bits, `set_extent_bit()` returns `-EEXIST` and identifies the failed range. Blocking lock wrappers then wait for those bits to clear and retry. Try-lock wrappers roll back any partially acquired range.

Clear operations can delete all bits with `EXTENT_CLEAR_ALL_BITS`, update changesets, split leading/trailing portions, wake lock waiters, and remove records whose state becomes zero.

`EXTENT_NOWAIT` is a control bit that switches allocations to `GFP_NOWAIT` and is masked out before state mutation. Other control bits drive accounting behavior but are not persisted as normal state bits.

For inode I/O trees, state mutation calls into inode delalloc hooks:
- `btrfs_set_delalloc_extent()`
- `btrfs_clear_delalloc_extent()`
- `btrfs_split_delalloc_extent()`
- `btrfs_merge_delalloc_extent()`

## State and Synchronization
Each `extent_io_tree` has a spinlock protecting the rb-tree. Each `extent_state` has a refcount and waitqueue. Waiting on extent bits is done by taking an extra state reference, preparing to wait on the state waitqueue, dropping the tree lock, scheduling, and retrying.

The optional cached-state pointer speeds repeated operations over adjacent ranges. Functions carefully drop stale cached references when state is no longer useful or when exclusive clear operations make caching unsafe.

Debug builds keep a global leak list for `extent_state` allocations and perform odd-range diagnostics for inode I/O trees.

## Risks
Inclusive range arithmetic is error-prone, especially at `end + 1`, `start - 1`, and `(u64)-1` sentinel boundaries.

Cached state references must be released exactly once and must not be trusted after unlock/retry unless the record is still in the tree.

Lock-bit records cannot be merged without breaking waitqueue semantics. Accidentally merging them could lose waiters or wake the wrong range.

Delalloc accounting is coupled to split/merge/set/clear paths for inode trees. Incorrect callback ordering can corrupt delayed allocation byte accounting, qgroup reservations, or inode byte updates.
