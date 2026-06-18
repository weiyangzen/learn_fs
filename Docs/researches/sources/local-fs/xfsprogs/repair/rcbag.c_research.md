# File Research: sources/local-fs/xfsprogs/repair/rcbag.c

## Role

`rcbag.c` implements an in-memory “refcount bag” used by rmap/refcount repair logic to track currently overlapping reverse mappings and derive shared refcount extents.

## Core Behavior

- `rcbag_init()` allocates the bag, reserves an in-memory xmbuf-backed btree sized for expected rmaps, and initializes the xfbtree.
- `rcbag_add()` inserts or increments a record keyed by `(startblock, blockcount, owner)`.
- `rcbag_count()` returns the total stacked item count.
- `rcbag_next_edge()` finds the next block boundary where the current sharing set changes.
- `rcbag_remove_ending_at()` removes all bag records ending at a block boundary and decrements the item count by their refcounts.
- `rcbag_ino_iter_*()` iterates distinct owners when at least two mappings are stacked.
- `rcbag_dump()` prints all records for debugging.

## Dependencies

It wraps `rcbag_btree.c`, xfbtree, xmbuf, libxfs btree cursors, repair error handling, and rmap record types.

## Risk Areas

- `nr_items` counts references, not simply distinct btree records; updates and removals must preserve that meaning.
- The code aborts on unexpected btree lookup/update/delete failures because this structure is internal repair state.
- Edge detection scans the whole bag to find the minimum ending block, which is simple but dependent on bag size.
