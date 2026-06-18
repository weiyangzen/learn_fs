# File Research: sources/os/linux/linux-stable/fs/btrfs/ordered-data.c

## Summary
Implements Btrfs ordered extent lifecycle management. Ordered extents track in-flight writes from logical file ranges to final metadata insertion, including COW/NOCOW/prealloc/compressed/direct/encoded variants, checksums, qgroup reservations, writeback completion, waiting, logging support, and splitting.

## Main Responsibilities
- Allocates and inserts ordered extents into per-inode rbtrees and per-root ordered lists.
- Tracks bytes left to write and marks ordered extents done/error/complete.
- Queues ordered extent completion work.
- Removes completed ordered extents and releases metadata/qgroup/accounting state.
- Waits ordered extents by inode range, root, all roots, or block-group disk range.
- Looks up ordered extents by point and range.
- Provides ordered extents to fsync logging.
- Locks file ranges while flushing overlapping ordered extents.
- Splits direct-I/O ordered extents for partial submitted ranges.
- Owns the ordered extent slab cache.

## Key APIs
- `btrfs_alloc_ordered_extent()`.
- `btrfs_add_ordered_sum()`.
- `btrfs_mark_ordered_extent_error()`.
- `btrfs_finish_ordered_extent()`.
- `btrfs_mark_ordered_io_finished()`.
- `btrfs_dec_test_ordered_pending()`.
- `btrfs_put_ordered_extent()`.
- `btrfs_remove_ordered_extent()`.
- `btrfs_wait_ordered_extents()`, `btrfs_wait_ordered_roots()`, `btrfs_wait_ordered_range()`.
- `btrfs_start_ordered_extent_nowriteback()`.
- `btrfs_lookup_ordered_extent()`, `btrfs_lookup_ordered_range()`, `btrfs_lookup_first_ordered_extent()`, `btrfs_lookup_first_ordered_range()`.
- `btrfs_get_ordered_extents_for_logging()`.
- `btrfs_lock_and_flush_ordered_range()`, `btrfs_try_lock_ordered_range()`.
- `btrfs_split_ordered_extent()`.
- `ordered_data_init()`, `ordered_data_exit()`.

## Important Behavior
Ordered extents are indexed in an inode rbtree by non-overlapping file ranges. Insert panics on overlap because overlap implies double allocation or accounting corruption. A cached `ordered_tree_last` accelerates repeated nearby lookups.

Allocation validates type flags, enforces relationships such as DIRECT not with COMPRESSED/ENCODED and ENCODED only with COMPRESSED, transfers or frees qgroup reservations depending on COW versus NOCOW/PREALLOC, grabs an inode reference, increments outstanding extents, initializes checksum/log/root/work lists, and inserts the object.

Finishing I/O decrements `bytes_left` under `ordered_tree_lock`. When it reaches zero, the code sets `BTRFS_ORDERED_IO_DONE`, wakes waiters, takes a completion-work reference, and queues work on either free-space or regular endio write workers. Failed COW writes set `BTRFS_INODE_COW_WRITE_ERROR` so fast fsync waits for ordered completion before logging extent maps that may point at unwritten extents.

Removal releases outstanding extent accounting, delalloc metadata, qgroup-related reservation state through lower layers, global ordered byte counters, rbtree membership, pending transaction wait accounting, root ordered-list membership, and waiters. It sets `BTRFS_ORDERED_COMPLETE` before waking waiters.

Root/all-root waiting splices ordered lists under locks, queues flush work for matching extents, waits for completion, and preserves skipped entries. Block-group filtering is by disk bytenr/disk length.

Range waiting starts writeback, waits page writeback, then walks ordered extents backward from the range end so all overlapping ordered extents complete before returning any saved writeback or ordered error.

Splitting creates a new ordered extent for the first `len` bytes, trims the original extent in place, moves matching checksum sums, preserves done/truncated state as needed, and updates root/inode structures under both root ordered lock and inode ordered-tree lock. Compressed extents and partially completed inconsistent extents cannot be split.

## State and Synchronization
Uses per-inode `ordered_tree_lock`, per-root `ordered_extent_lock` and `ordered_extent_mutex`, filesystem `ordered_root_lock` and `ordered_operations_mutex`, ordered extent wait queues, completions, workqueues, refcounts, and transaction pending ordered counters.

References are held by callers, the rbtree, logging lists, completion work, and wait/flush paths. The final put schedules delayed iput for the inode and frees checksum sums before returning the ordered extent to the slab.

## Risks
This file is concurrency- and accounting-heavy. Bugs can corrupt extent accounting, leak qgroup reservations, race transaction commit pending ordered waits, expose unwritten COW extents to fsync logging, or deadlock extent locking/writeback.

The split path deliberately updates an existing rbtree key range without removing the original node because ordering remains valid. That relies on strict preconditions: split length is within the extent, the extent is not compressed, disk and logical lengths match, and partial completion state is consistent.
