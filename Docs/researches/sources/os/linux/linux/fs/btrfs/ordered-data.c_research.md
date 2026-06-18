# File Research: sources/os/linux/linux/fs/btrfs/ordered-data.c

This file implements Btrfs ordered extents: in-memory records for writes whose data I/O has been submitted or is pending and whose file extent/checksum metadata still needs finalization.

Core data model:
- Each inode owns an rbtree of `btrfs_ordered_extent` records keyed by file offset.
- Each root also has an ordered extent list, and filesystem-wide `ordered_roots` tracks roots with pending ordered extents.
- Ordered extents track file range, disk range, ram bytes, compression type, qgroup reservation, checksums, bytes left to write, flags, refs, waitqueue, work items, and root/log list links.
- A slab cache stores ordered extent objects.

Creation and insertion:
- `alloc_ordered_extent()` validates type flags, handles qgroup data reservation transfer/freeing, initializes the object, grabs the inode, and increments outstanding extent accounting.
- `btrfs_alloc_ordered_extent()` adapts `struct btrfs_file_extent` details for regular, NOCOW, PREALLOC, compressed, encoded, and direct I/O cases.
- `insert_ordered_extent()` inserts into the inode rbtree, panics on overlap, increments `ordered_bytes`, and links the entry to the root and filesystem root lists.

I/O completion:
- `can_finish_ordered_extent()` subtracts completed bytes from `bytes_left`, marks I/O errors, sets `BTRFS_ORDERED_IO_DONE` when all data I/O is finished, wakes waiters, and takes a ref for finish work.
- `btrfs_finish_ordered_extent()` handles one completion range and queues metadata finalization work when complete.
- `btrfs_mark_ordered_io_finished()` walks all ordered extents intersecting a range and marks the corresponding portions done.
- `btrfs_dec_test_ordered_pending()` is an older/cached single-extent decrement helper used by completion paths that must atomically test final completion.
- Failed COW writes set `BTRFS_INODE_COW_WRITE_ERROR` so fast fsync waits for ordered completion before logging stale extent maps.

Removal and lifetime:
- `btrfs_remove_ordered_extent()` removes an extent from the inode rbtree and root lists, releases delayed allocation metadata, decrements ordered byte accounting and outstanding extents, handles transaction `pending_ordered` wakeups, sets `BTRFS_ORDERED_COMPLETE`, and wakes extent waiters.
- `btrfs_put_ordered_extent()` drops refs, schedules delayed inode iput, frees checksum records, and returns the object to the slab cache.
- `btrfs_add_ordered_sum()` appends checksum records to an ordered extent.
- `btrfs_mark_ordered_extent_error()` marks the extent and sets mapping error.

Waiting and flushing:
- `btrfs_wait_ordered_extents()` starts and waits for up to `nr` ordered extents in a root, optionally filtered by block group disk range.
- `btrfs_wait_ordered_roots()` iterates filesystem roots with pending ordered extents.
- `btrfs_start_ordered_extent_nowriteback()` starts writeback for dirty pages except an optional excluded range, then waits for `BTRFS_ORDERED_COMPLETE`.
- `btrfs_wait_ordered_range()` starts writeback and waits all ordered extents overlapping a file range, preserving writeback errors after waiting.
- `btrfs_lock_and_flush_ordered_range()` locks an extent range and repeatedly flushes overlapping ordered extents until none remain.
- `btrfs_try_lock_ordered_range()` implements the nonblocking variant.

Lookup and logging:
- `btrfs_lookup_ordered_extent()`, `btrfs_lookup_ordered_range()`, `btrfs_lookup_first_ordered_extent()`, and `btrfs_lookup_first_ordered_range()` provide refcounted ordered extent lookup variants.
- `btrfs_get_ordered_extents_for_logging()` collects not-yet-logged ordered extents for fsync logging while the inode is locked.

Splitting:
- `btrfs_split_ordered_extent()` splits the first `len` bytes of a non-compressed ordered extent into a new ordered extent.
- It rejects zero-length/oversized splits, errored extents, partially completed inconsistent extents, and compressed extents.
- The split moves checksum records for the first range, adjusts disk/file fields, preserves truncated state, and updates root/inode structures under both root ordered lock and inode ordered tree lock.

Important invariants:
- Ordered extents for an inode must never overlap.
- Exactly one exclusive type flag must be set among regular, NOCOW, PREALLOC, and compressed.
- Direct I/O cannot be combined with compressed or encoded flags.
- Encoded ordered extents must also be compressed.
- Metadata completion is distinct from data I/O completion: `IO_DONE` means data I/O finished, `COMPLETE` means the ordered extent was removed after metadata work.
- Transaction commit waiters rely on `BTRFS_ORDERED_PENDING` and `pending_ordered` accounting.
- Free-space inode ordered extents avoid some lockdep annotations because their wait context differs.

Cross-file relationships:
- Public structures and prototypes are in `ordered-data.h`.
- Final metadata insertion is performed by `btrfs_finish_ordered_io()` / `btrfs_finish_one_ordered()` declared here and implemented elsewhere.
- Integrates with delalloc-space metadata release, qgroup accounting, compressed I/O, direct I/O, fsync logging, writeback, transaction commit, and block-group relocation/waiting.
