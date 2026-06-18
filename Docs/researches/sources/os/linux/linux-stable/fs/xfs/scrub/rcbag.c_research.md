# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag.c

This file implements a “refcount bag”: an in-memory btree-backed multiset of reverse-map extents used to compute refcount edge changes.

State:
- `struct rcbag` stores mount, in-memory `xfbtree`, and a logical item count.

Operations:
- `rcbag_init` allocates the bag and initializes the in-memory btree.
- `rcbag_free` destroys the btree and frees state.
- `rcbag_add` inserts an rmap start/blockcount pair or increments its record refcount.
- `rcbag_count` returns the total item count.
- `rcbag_next_edge` finds the next block where refcount can change, considering the next rmap start and the ending block of all active bag records.
- `rcbag_remove_ending_at` removes all bag records whose end equals a given block and decrements item count by their stored refcount.
- `rcbag_dump` prints all records for diagnostics.

The bag is keyed by `(startblock, blockcount)` and stores a refcount for identical rmap intervals. Transactions against the in-memory btree are committed/canceled with `xfbtree_trans_commit` and `xfbtree_trans_cancel`.
