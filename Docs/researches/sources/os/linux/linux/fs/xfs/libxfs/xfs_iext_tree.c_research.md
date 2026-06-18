# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_iext_tree.c

This file implements the in-core extent index used by XFS inode forks. It stores `xfs_bmbt_irec` mappings in compact `xfs_iext_rec` records and organizes them as a small 256-byte-node B-tree with linked leaves. The packed record layout preserves start offset, block count, start block, and unwritten state in two 64-bit words.

Major responsibilities:
- Encode/decode extent records via `xfs_iext_set` and `xfs_iext_get`.
- Traverse extent lists with cursor APIs: `xfs_iext_first`, `xfs_iext_last`, `xfs_iext_next`, and `xfs_iext_prev`.
- Locate mappings with `xfs_iext_lookup_extent`, `xfs_iext_lookup_extent_before`, and `xfs_iext_get_extent`.
- Mutate the tree with `xfs_iext_insert_raw`, `xfs_iext_insert`, `xfs_iext_remove`, and `xfs_iext_update_extent`.
- Grow, split, merge, and shrink internal/leaf nodes while keeping parent keys synchronized.
- Destroy the in-core tree through `xfs_iext_destroy`.

Important invariants:
- `if_bytes` counts extent-record bytes and drives `xfs_iext_count`.
- `if_height == 0` means no tree; `if_height == 1` is a single leaf/root; larger heights have inner nodes.
- Empty records are identified by `hi == 0`, relying on the fact that valid extents cannot have zero length.
- Leaf nodes are doubly linked to support efficient cursor movement.
- Mutations increment `if_seq` with `WRITE_ONCE`, notably for COW fork change detection in writeback paths.

Dependencies and integration:
- Operates on `struct xfs_ifork`, `struct xfs_iext_cursor`, and `struct xfs_bmbt_irec`.
- Exposes APIs declared in `xfs_inode_fork.h`.
- Uses tracing hooks around insert/remove/update operations.
- Used by inode fork formatting, bmap operations, delayed allocation, and COW fork management.

Risk notes:
- Correctness depends on careful key propagation when the first record of a leaf/node changes.
- Split and merge code assumes sorted records and valid cursor placement.
- Allocation uses no-fail kernel allocations, appropriate for core metadata paths but important for memory-pressure analysis.
