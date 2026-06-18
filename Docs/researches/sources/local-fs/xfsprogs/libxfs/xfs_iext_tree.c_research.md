# File Research: sources/local-fs/xfsprogs/libxfs/xfs_iext_tree.c

## Role

This file implements XFS's in-core inode extent tree for `libxfs`. It stores `xfs_bmbt_irec` mappings in a compact 128-bit in-memory record format and provides cursor-based insertion, removal, lookup, update, iteration, and destruction for inode forks.

It is the data structure behind the incore extent lists used by data, attribute, and CoW forks. The on-disk mapping format is still the bmap extent or btree format; this file is only the in-memory search/update structure.

## Main Structures

- `struct xfs_iext_rec` packs start offset, block count, start block, and unwritten state into two 64-bit words.
- `struct xfs_iext_leaf` stores packed extent records and links neighboring leaves with `prev` / `next`.
- `struct xfs_iext_node` stores lookup keys and child pointers for internal levels.
- `struct xfs_iext_cursor` points to a leaf and record position.

The tree uses fixed 256-byte nodes. Height zero means empty. Height one means the root is a leaf-like record array. Larger heights use internal nodes above linked leaves.

## Core Operations

- `xfs_iext_count` returns extent count from fork byte count.
- `xfs_iext_first`, `xfs_iext_last`, `xfs_iext_next`, and `xfs_iext_prev` implement ordered cursor movement.
- `xfs_iext_lookup_extent` finds the extent covering an offset, or the first extent after it.
- `xfs_iext_lookup_extent_before` finds the last extent before an end offset.
- `xfs_iext_get_extent` expands the cursor record into `xfs_bmbt_irec`.
- `xfs_iext_insert_raw` inserts a record into a fork extent tree.
- `xfs_iext_insert` wraps raw insert with inode/fork-state selection and tracing.
- `xfs_iext_remove` deletes the cursor record and rebalances/free nodes as needed.
- `xfs_iext_update_extent` overwrites a cursor record and updates parent keys if the start offset changes.
- `xfs_iext_destroy` recursively frees the tree and resets the fork.

## Tree Mutation Details

Insertion grows an empty fork into a root, reallocates a height-one root as it grows, splits full leaves, and propagates new leaf keys into parent nodes. Sequential appends get a fast split path that spills into a new node without copying half the old contents.

Removal shifts records left, clears the last record, decrements `if_bytes`, updates parent keys when the first record changes, and merges underfull leaves or internal nodes when possible. A root with one child collapses down a level.

## Invariants

- An empty record is detected by `hi == 0`; valid extents cannot have zero length.
- Parent keys track the first start offset under each child.
- Cursor validity depends on both bounds and non-empty records.
- The fork sequence counter is incremented before extent tree mutations so CoW/writeback code can notice changes.
- The compact record layout assumes bmap field bit widths: 54-bit file offset, 21-bit block count, 52-bit startblock, and one unwritten bit.
- Memory allocation uses no-fail kernel-style allocation wrappers in userspace.

## Dependencies

This file depends on `xfs_ifork`, `xfs_bmbt_irec`, bmap fork state flags, tracing hooks, statistics, and basic XFS bit masks. Higher-level mapping code in `xfs_bmap.c` relies on this tree for all in-core extent cache mutations.

## Research Notes

The most important correctness risk is keeping parent keys, leaf links, cursor position, and `if_bytes` synchronized during splits, merges, and first-record updates. This file intentionally avoids on-disk accounting; callers must separately update fork extent counts, transaction logging, quota, rmap, and btree state.
