# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent-io-tree.c

## Role

Implements Btrfs extent state trees: red-black trees of byte ranges tagged with state bits such as dirty, locked, delalloc, boundary, qgroup reserved, and device-allocation state. The file provides range set/clear/convert/test/find/count/lock operations with range splitting, merging, cached-state optimization, wait queues for locked ranges, changeset accounting, and debug leak tracking.

## Data Model

- `struct extent_io_tree` owns an rb-tree of `struct extent_state` records and a spinlock.
- `struct extent_state` stores an inclusive `[start, end]` byte range, rb-node, wait queue, refcount, and state bitmask.
- Adjacent states with identical mergeable bitmasks are merged unless they contain lock bits or boundary bits.
- For inode I/O trees, state changes are mirrored into delalloc accounting through `btrfs_set_delalloc_extent()`, `btrfs_clear_delalloc_extent()`, `btrfs_split_delalloc_extent()`, and `btrfs_merge_delalloc_extent()`.
- `extent_changeset` integration counts changed bytes and can record changed ranges in a ulist.

## Allocation and Debugging

- `btrfs_extent_state_init_cachep()` creates the `btrfs_extent_state` slab cache.
- `btrfs_extent_state_free_cachep()` checks debug leaks and destroys the cache.
- `alloc_extent_state()` masks unsupported GFP flags, allocates a state, initializes rb-node/refcount/waitqueue/state, registers debug leak tracking, and traces allocation.
- `btrfs_free_extent_state()` decrements the state reference and frees only when it reaches zero, warning if the state is still in a tree.
- Under `CONFIG_BTRFS_DEBUG`, leaked states are kept on a global list and reported with range/state/refcount information.
- `btrfs_debug_check_extent_io_range()` warns about suspicious inode I/O ranges in debug builds.

## Tree Search and Structural Helpers

- `tree_search_for_insert()` finds a state containing an offset or the first state after the offset, and can return rb insertion position.
- `tree_search_prev_next()` finds a containing state or previous/next neighbors.
- `tree_search()` is the inexact search wrapper.
- `next_state()` and `prev_state()` navigate rb-tree neighbors.
- `merge_prev_state()`, `merge_next_state()`, and `merge_state()` combine adjacent compatible states and update inode delalloc accounting when relevant.
- `insert_state()` inserts a new state and can merge it into adjacent states.
- `insert_state_fast()` inserts at a known rb position and merges.
- `split_state()` splits an existing state at a byte offset using a preallocated state for the lower half.
- `state_wake_up()` wakes waiters when lock bits are cleared.
- `set_gfp_mask_from_bits()` interprets `EXTENT_NOWAIT` as `GFP_NOWAIT` and strips it from the state bits.

## Clearing Bits

`btrfs_clear_extent_bit_changeset()` clears bits over an inclusive range:

- It optionally treats `EXTENT_CLEAR_ALL_BITS` as deleting all non-control bits.
- Clearing `EXTENT_DELALLOC` also includes `EXTENT_NORESERVE`.
- It uses cached states when possible, searches for overlapping records, splits records at range boundaries, clears target bits, wakes lock waiters, removes states that become empty, and merges remaining compatible states.
- It contains optimized paths for clearing an entire suffix/prefix without allocating a split state when all bits would be removed.
- It supports nowait allocation semantics through `EXTENT_NOWAIT`.
- `btrfs_clear_extent_bit()` and `btrfs_unlock_extent()` are inline wrappers declared in the header, while `btrfs_clear_record_extent_bits()` records changed ranges.

## Setting and Converting Bits

- `set_extent_bit()` is the core range setter. It handles holes, overlapping states, splits, mergeable insertions, cached states, optional changesets, and exclusive lock bits.
- Exclusive lock bits return `-EEXIST` with the failing start offset and optional failed state when the requested range overlaps an already locked state.
- `btrfs_set_extent_bit()` is the public plain setter.
- `btrfs_set_record_extent_bits()` sets non-lock bits while recording changed ranges.
- `btrfs_convert_extent_bit()` sets one set of bits and clears another over a range, intended for mergeable state transitions such as delalloc to dirty. It is not intended for lock/boundary semantics.

## Waiting and Locking

- `wait_extent_bit()` waits for one or more bits to clear in a range, using per-state wait queues and keeping a referenced failed/cached state while sleeping.
- `btrfs_try_lock_extent_bits()` attempts to set lock bits without waiting. If it partially locked a prefix before an existing lock, it clears that prefix and returns false.
- `btrfs_lock_extent_bits()` sets lock bits and waits/retries on `-EEXIST`, clearing any partial prefix before waiting.
- `btrfs_next_extent_state()` returns a referenced next state for contexts where no concurrent tree modification is expected.

## Query Operations

- `btrfs_find_first_extent_bit()` finds the first state with any requested bit set at or after a start offset and can cache the found state for repeated iteration.
- `btrfs_find_contiguous_extent_bit()` finds the full contiguous range covered by states with given bits, used when temporary splits may hide the true contiguous extent.
- `btrfs_find_delalloc_range()` finds a contiguous delalloc range up to `max_bytes`, stopping at holes or `EXTENT_BOUNDARY`.
- `btrfs_find_first_clear_extent_bit()` returns the first range at or after a start offset where requested bits are not set, treating holes as clear ranges and using `-1` as open-ended end.
- `btrfs_count_range_bits()` counts bytes in a range where all requested bits are set, optionally requiring contiguity and supporting cached state reuse.
- `btrfs_test_range_bit_exists()` tests whether a single bit exists anywhere in a range.
- `btrfs_get_range_bits()` ORs together all state bits found in a range and caches the first state.
- `btrfs_test_range_bit()` tests whether a half-open range `[start, end)` is continuously covered by states with a single bit set.

## Lifecycle

- `btrfs_extent_io_tree_init()` initializes an empty tree, lock, owner, and fs_info/inode pointer.
- `btrfs_extent_io_tree_release()` empties a tree after callers guarantee no concurrent access, asserts no lock bits or waiters, clears rb nodes, frees states, and verifies the tree stayed empty.

## Concurrency and Error Handling

- `tree->lock` protects all rb-tree mutations, state bits, wait queue enrollment/removal, and cached-state validity checks.
- Potentially blocking allocations are done outside the spinlock, with atomic allocation attempts inside locked sections and retry paths when allocation fails.
- `cond_resched_lock()` and explicit search retries avoid long lock holds over large trees.
- Structural inconsistencies in insert/split/changeset handling call `extent_io_tree_panic()`, which maps the tree back to `fs_info` for a Btrfs panic.

## Dependencies

Uses Linux slab, rb-tree, spinlock, waitqueue, refcount, and Btrfs tracepoints. It integrates with Btrfs inode delalloc accounting, extent changesets, and the broader extent I/O layer.

## Research Notes

This file is the generic range-state engine behind many Btrfs byte-range operations. The implementation is careful about three competing constraints: preserving exact range state through splits, keeping the tree compact through merging, and supporting lock-like bits that require wait/wakeup semantics and cannot be freely merged with ordinary dirty/delalloc state.
