# File Research: sources/local-fs/kdave-linux/fs/btrfs/ordered-data.c

## Purpose

`ordered-data.c` manages Btrfs ordered extents: the in-memory records that track outstanding writes from allocation/writeback through I/O completion, checksum insertion, metadata completion, fsync logging, transaction waiting, and cleanup.

## Data Structures and Storage

Ordered extents are stored per inode in an rb-tree keyed by file offset, with `ordered_tree_last` as a lookup cache. Each extent is also linked into a per-root ordered extent list, and roots with pending extents are linked into `fs_info->ordered_roots`. Objects are allocated from the `btrfs_ordered_extent_cache` slab.

`entry_end()`, `tree_insert()`, `__tree_search()`, `ordered_tree_search()`, and range-overlap helpers implement non-overlapping rb-tree storage and lookup.

## Allocation and Insertion

`btrfs_alloc_ordered_extent()` validates type flags, handles regular/COW/NOCOW/PREALLOC/COMPRESSED/ENCODED/DIRECT combinations, releases or transfers qgroup reservations, initializes refs/lists/waits/completion/work, increments outstanding extents, and inserts the extent into both inode and root/global tracking structures.

`btrfs_add_ordered_sum()` appends checksum records to an ordered extent.

## I/O Completion

`can_finish_ordered_extent()` decrements `bytes_left`, records I/O errors, sets `BTRFS_ORDERED_IO_DONE` when all data is done, wakes waiters, traces completion, and takes a ref for queued finish work.

`btrfs_finish_ordered_extent()` and `btrfs_mark_ordered_io_finished()` are endio-facing helpers. The range version can walk multiple ordered extents in a finished I/O range. On COW write error, the inode gets `BTRFS_INODE_COW_WRITE_ERROR` so fast fsync will wait for completion before logging possibly stale extent maps.

`btrfs_dec_test_ordered_pending()` supports callers that complete one ordered extent range and optionally cache the finished extent.

## Removal and Lifetime

`btrfs_remove_ordered_extent()` removes an extent from the inode rb-tree and root list, updates outstanding extent/delalloc/ordered-byte accounting, marks completion, handles transaction `pending_ordered` wakeups, releases lockdep maps, and wakes waiters. It does not drop refs itself.

`btrfs_put_ordered_extent()` frees an extent when refs reach zero, after asserting it is no longer linked in root/log/rb-tree structures. It schedules delayed iput and frees checksum sums.

## Waiting and Flushing

`btrfs_wait_ordered_extents()` splices a root’s ordered list, selects extents optionally intersecting a block group range, queues flush work, waits for each completion, and restores skipped/spliced entries. `btrfs_wait_ordered_roots()` iterates roots in the global ordered-root list.

`btrfs_start_ordered_extent_nowriteback()` starts writeback for dirty pages in the ordered extent range unless direct I/O, then waits for `BTRFS_ORDERED_COMPLETE`. A no-writeback subrange can be excluded.

`btrfs_wait_ordered_range()` starts writeback, waits for page writeback, then walks ordered extents backward through the requested range until all relevant extents complete, preserving writeback errors.

Range lock helpers `btrfs_lock_and_flush_ordered_range()` and `btrfs_try_lock_ordered_range()` coordinate extent locking with pending ordered extents.

## Lookup and Logging

Lookup helpers include exact-offset, first-before/around-offset, first-overlapping-range, and any-overlapping-range variants. `btrfs_get_ordered_extents_for_logging()` collects not-yet-logged ordered extents in file-offset order for fsync logging and takes refs.

## Splitting

`btrfs_split_ordered_extent()` splits the first `len` bytes from a non-compressed ordered extent into a new ordered extent. It rejects errors, compressed extents, invalid lengths, and partially completed inconsistent extents. It adjusts offsets, disk ranges, lengths, bytes-left, truncation state, checksum sums, and inserts the new extent while holding both root ordered extent lock and inode ordered tree lock.

## Dependencies and Risk Notes

The file integrates with transactions, qgroups, delalloc space, compression, extent I/O, file writeback, block groups, and Btrfs workqueues. Correctness depends on rb-tree non-overlap, refcount ownership, lock ordering, delayed metadata completion, and exact accounting of `bytes_left`, qgroup reservations, delalloc metadata, and root ordered lists.
