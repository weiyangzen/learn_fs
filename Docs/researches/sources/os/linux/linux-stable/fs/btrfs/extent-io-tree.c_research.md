# File Research: sources/os/linux/linux-stable/fs/btrfs/extent-io-tree.c

## Purpose
Implements Btrfs extent state trees: rbtrees of byte ranges tagged with state bits such as dirty, locked, delalloc, qgroup-reserved, device allocated/trimmed, and related control flags. These trees are used by inode IO, btree metadata IO, transaction dirty page tracking, pinned extents, excluded extents, log ranges, relocation, and device allocation state.

## Core Model
- Each `extent_io_tree` owns an rb-tree of non-overlapping `extent_state` records.
- Each `extent_state` covers an inclusive `[start, end]` range and has a bitmask, waitqueue, refcount, and rb node.
- Adjacent states with identical mergeable state are coalesced. States with lock bits or `EXTENT_BOUNDARY` are not merged.
- Inode-owned trees call delalloc accounting hooks when states are set, cleared, split, or merged.

## Allocation And Lifetime
- Uses a slab cache `extent_state_cache`.
- `btrfs_extent_state_init_cachep()` creates the cache; `btrfs_extent_state_free_cachep()` checks debug leaks and destroys it.
- `alloc_extent_state()` initializes rb node, waitqueue, refcount, debug tracking, and tracing.
- `btrfs_free_extent_state()` decrements refs and frees only when the state is no longer referenced.
- Debug builds maintain a global leak list and validate suspicious inode IO ranges.
- `btrfs_extent_io_tree_init()` initializes an empty tree, lock, owner, and fs/inode pointer.
- `btrfs_extent_io_tree_release()` empties a tree after all external access has stopped; it asserts no lock bits and no waiters remain.

## Search And Tree Helpers
- `tree_search_for_insert()` finds the state containing an offset or the next state after it, and can return rb insert parent/link pointers.
- `tree_search_prev_next()` finds containing, previous, and next states for clear-range discovery.
- `next_state()` and `prev_state()` wrap rb traversal.
- `merge_prev_state()`, `merge_next_state()`, and `merge_state()` coalesce compatible adjacent ranges.
- `split_state()` splits an existing state at a byte offset using a preallocated state for one side.

## Setting Bits
- `set_extent_bit()` is the internal range setter used by most public set/lock APIs.
- It handles holes, exact matches, leading splits, trailing splits, insertion, merging, cached states, NOWAIT allocation semantics, and exclusive lock-bit conflicts.
- `btrfs_set_extent_bit()` is the basic public setter.
- `btrfs_set_record_extent_bits()` sets bits while recording changed byte counts/ranges in an `extent_changeset`; lock bits are intentionally unsupported for this wrapper.
- `set_state_bits()` strips control bits before setting state and performs inode delalloc accounting plus changeset accounting.

## Clearing Bits
- `btrfs_clear_extent_bit_changeset()` clears a bit range, splitting states when needed, deleting empty states, waking lock waiters, merging remaining states, handling `EXTENT_CLEAR_ALL_BITS`, and optionally recording changes.
- `btrfs_clear_record_extent_bits()` is the changeset-recording clear wrapper.
- `clear_state_bit()` performs the per-state clear, wakeup, deletion/merge, and next-state selection.
- If `EXTENT_DELALLOC` is cleared, `EXTENT_NORESERVE` is also included for accounting consistency.

## Locking Semantics
- `btrfs_try_lock_extent_bits()` attempts to set lock bits; on conflict it clears any partial lock already taken and returns false.
- `btrfs_lock_extent_bits()` loops until it can set the requested lock bits, waiting via `wait_extent_bit()` when another state already has those exclusive bits.
- `wait_extent_bit()` attaches to the state waitqueue under the tree lock, sleeps uninterruptibly, and retries after wakeup.
- Lock waiters are woken by `state_wake_up()` when `EXTENT_LOCKED` or `EXTENT_DIO_LOCKED` bits are cleared.

## Conversion And Queries
- `btrfs_convert_extent_bit()` atomically sets one set of bits and clears another across a range, intended only for mergeable states such as delalloc-to-dirty conversion.
- `btrfs_find_first_extent_bit()` finds the first state with any requested bit and supports cached iteration.
- `btrfs_find_contiguous_extent_bit()` returns the full contiguous area covered by a bit, used when temporary splitting may hide real contiguity.
- `btrfs_find_delalloc_range()` finds a contiguous delalloc range up to `max_bytes`, stopping at boundaries or non-delalloc states.
- `btrfs_find_first_clear_extent_bit()` finds the first range lacking requested bits, treating holes as clear.
- `btrfs_count_range_bits()` counts bytes that have all requested bits, optionally requiring contiguity and supporting cached state.
- `btrfs_test_range_bit_exists()` checks if a single bit exists anywhere in a range.
- `btrfs_get_range_bits()` ORs all bits present across a range and caches the first state.
- `btrfs_test_range_bit()` verifies that a whole half-open range is continuously covered by a single bit.
- `btrfs_next_extent_state()` returns a referenced next state for contexts where concurrent modification is known not to happen.

## Changeset Accounting
`add_extent_changeset()` increments `bytes_changed` and optionally records changed ranges in a ulist. It avoids counting no-op set/clear operations and panics through `extent_io_tree_panic()` if changeset insertion fails in paths that cannot safely recover.

## Concurrency And Allocation Strategy
- All tree mutation and lookup happen under `tree->lock`.
- Range operations preallocate extent states before locking when possible, retry after dropping the lock if atomic allocation fails, and reschedule on long scans.
- `EXTENT_NOWAIT` switches allocation to `GFP_NOWAIT`; otherwise operations use `GFP_NOFS`.
- Cached-state pointers are reference-counted and freed/replaced carefully to avoid repeated tree searches across adjacent operations.

## Relationship To Other Files
- `disk-io.c` uses these helpers to track and clean transaction dirty pages and pinned extents during transaction abort and unmount.
- Inode and writeback paths use lock/delalloc/dirty state management for page and ordered extent coordination.
- Device allocation code aliases `EXTENT_DIRTY` and `EXTENT_DEFRAG` as chunk allocation/trim state bits through the header.
