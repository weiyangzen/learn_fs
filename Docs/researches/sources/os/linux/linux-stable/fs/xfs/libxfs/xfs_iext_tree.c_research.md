# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_iext_tree.c

## Role
`xfs_iext_tree.c` implements the in-core extent index used by XFS inode forks. It stores `struct xfs_bmbt_irec` mappings in a compact 256-byte node/leaf tree, supports cursor-based traversal and lookup, and provides insert, remove, update, and destroy operations for data, attr, and CoW forks.

## Main Responsibilities
- Pack and unpack in-core extent records into `struct xfs_iext_rec`, preserving start offset, start block, block count, and unwritten-state bit.
- Maintain a small btree-like structure with internal nodes keyed by the first extent offset of each child and leaves containing packed extent records plus prev/next leaf links.
- Provide cursor movement helpers: `xfs_iext_first`, `xfs_iext_last`, `xfs_iext_next`, and `xfs_iext_prev`.
- Support lookups by file offset through `xfs_iext_lookup_extent` and reverse/range-end lookup through `xfs_iext_lookup_extent_before`.
- Insert, split, merge, remove, and rebalance leaves and internal nodes while keeping parent keys current.
- Increment `if_seq` before extent-tree mutations so writeback and CoW fork users can notice changes.

## Important Functions
- `xfs_iext_set` and `xfs_iext_get` are the only packing/unpacking boundary for in-core extent records.
- `xfs_iext_find_level` descends to the requested tree level using separator keys.
- `xfs_iext_insert_raw` allocates the first root, grows the inline root, splits full leaves, inserts a record, and propagates new child nodes upward.
- `xfs_iext_insert_node` and `xfs_iext_split_node` maintain internal levels after leaf splits.
- `xfs_iext_remove` deletes the current cursor record, fixes cursor position, updates parent keys, and triggers leaf/node rebalance or root removal.
- `xfs_iext_rebalance_leaf`, `xfs_iext_remove_node`, and `xfs_iext_rebalance_node` merge underfull nodes when combined entries fit.
- `xfs_iext_update_extent` overwrites an existing extent and repairs separator keys if the first record offset changes.
- `xfs_iext_destroy` recursively frees the tree and resets the fork’s extent-tree fields.

## Data and Invariants
- `if_bytes` counts packed in-core extent records, not allocated tree-node bytes.
- `if_height == 0` means no tree; `if_height == 1` means `if_data` points directly at a leaf/root record area; higher values use internal nodes.
- Empty extent records are detected by `hi == 0`; zero-length extents are impossible, so this is a safe sentinel.
- Internal node keys are first offsets of child subtrees; `XFS_IEXT_KEY_INVALID` marks unused slots.
- Leaves are linked in sorted order to make adjacent cursor movement cheap after lookup.
- The tree is optimized for append patterns: splitting at the end spills into a new empty node rather than moving half the entries.

## Error Handling and Risks
- Allocation uses `__GFP_NOFAIL`, so tree operations do not return allocation errors.
- Corruption-style conditions are enforced with assertions because this is in-memory metadata derived from already-verified fork mappings.
- The recursive destroy path is explicitly noted as stack-sensitive.

## Dependencies
This file depends on inode fork state from `xfs_inode_fork.h`, bmap extent records, XFS tracepoints, and bmap fork-state flags via `xfs_iext_state_to_fork`.

## Research Notes
This is not an on-disk btree. It is a compact in-memory acceleration structure for inode fork extents, with parent keys keyed by first child extent offset and leaf links for efficient sequential scans.
