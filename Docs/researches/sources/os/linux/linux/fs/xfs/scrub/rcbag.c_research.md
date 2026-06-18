# File Research: sources/os/linux/linux/fs/xfs/scrub/rcbag.c

## Role
Implements a refcount bag: an in-memory btree-backed multiset of reverse-mapping extents used to compute sharing/refcount transitions.

## Lifecycle
- `rcbag_init` allocates a bag and initializes an in-memory `xfbtree`.
- `rcbag_free` destroys the tree and clears the caller’s pointer.

## Operations
- `rcbag_add` inserts an rmap extent or increments the record refcount if the same start/length already exists.
- `rcbag_count` returns the total item count, including duplicate refcounts.
- `rcbag_next_edge` finds the next block where refcount state can change, considering both the next incoming rmap and tracked bag entries ending.
- `rcbag_remove_ending_at` deletes all records ending at a specified block and decrements item count by their refcounts.
- `rcbag_dump` emits diagnostic records.

## Risk Points
- Every mutation commits or cancels the backing `xfbtree` transaction.
- Tree cursor failures are treated as corruption because this is repair scratch state.
