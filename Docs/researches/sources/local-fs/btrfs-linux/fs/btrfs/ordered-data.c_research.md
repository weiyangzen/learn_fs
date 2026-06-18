# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ordered-data.c

## Purpose

Implements ordered extent tracking: the bridge between submitted file data I/O and later metadata insertion/accounting completion. Ordered extents record pending writes by inode range, disk extent, qgroup reservation, checksum list, completion state, and root-level pending ordered lists.

## Main Responsibilities

- Allocates ordered extent objects from a slab cache.
- Inserts non-overlapping ordered extents into per-inode rb-trees and per-root ordered lists.
- Tracks ordered bytes globally and outstanding extents per inode.
- Stores checksum lists for later metadata insertion.
- Marks ordered I/O progress, handles errors, and queues finish work when all bytes complete.
- Removes completed ordered extents from inode/root tracking and wakes transaction/order waiters.
- Starts and waits ordered extents by root, filesystem, block group, or inode range.
- Looks up ordered extents by exact offset, first-before/near offset, or overlapping range.
- Provides ordered extent lists for logging/fsync.
- Locks and flushes ranges until no ordered extents overlap.
- Splits non-compressed ordered extents, moving checksum records and adjusting disk/file ranges.
- Initializes/destroys the ordered extent slab cache.

## Key Behaviors and Invariants

- Ordered extents in an inode rb-tree must not overlap; insertion panics on overlap.
- Exactly one exclusive type flag must be set: regular, nocow, prealloc, or compressed.
- Encoded extents must also be compressed; direct I/O cannot be compressed or encoded.
- NOCOW/PREALLOC qgroup reservations are freed immediately; COW reservations transfer to the ordered extent until completion.
- `bytes_left` is the gate for setting `BTRFS_ORDERED_IO_DONE`; completion work is queued once.
- Write errors set `BTRFS_ORDERED_IOERR` and propagate mapping error; COW write errors also mark the inode to force future fast fsync to wait for ordered completion.
- Removal clears rb-tree state, root list membership, ordered counters, metadata reservations, pending transaction ordered counts, and wakes waiters.
- Waiting roots splices lists under locks, queues flush work, and restores skipped/spliced list entries.
- `btrfs_lock_and_flush_ordered_range()` repeatedly locks the extent range, checks for overlap, unlocks and waits if needed, and returns with the range locked and no overlapping ordered extent.
- Splitting refuses compressed, errored, zero-length, partially inconsistent, or disk/file length-mismatched ordered extents.

## Dependencies

Uses transaction lockdep annotations, inode/root ordered locks, qgroup accounting, delalloc metadata reservation, extent locking, workqueues, page writeback, block-group range filtering, tracing, and delayed iput.
