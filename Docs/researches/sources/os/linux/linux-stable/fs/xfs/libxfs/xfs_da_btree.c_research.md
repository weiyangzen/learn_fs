# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_da_btree.c

## Role
`xfs_da_btree.c` is the shared directory/attribute btree engine for XFS. It manages hashed-name btrees used by large directories and extended attributes, including node creation, lookup traversal, split/join rebalancing, sibling list maintenance, logical-to-physical buffer mapping, and block allocation/removal.

## Main Responsibilities
- Allocate, reset, and free `struct xfs_da_state` search/split state through `xfs_da_state_alloc`, `xfs_da_state_reset`, and `xfs_da_state_free`.
- Abstract v2/v3 node headers through `xfs_da3_node_hdr_from_disk` and `xfs_da3_node_hdr_to_disk`.
- Verify DA block metadata for magic values, CRC-era UUID/block/LSN fields, owner checks, node level, and entry count limits.
- Read DA node buffers and dynamically dispatch leaf-looking buffers to attr or directory leaf verifiers when the caller expected a node.
- Grow and shrink directory/attribute btrees through split, root split, join, root join, node rebalance/unbalance, and sibling link/unlink helpers.
- Traverse the btree for lookups using hashed names and duplicate-hash aware descent.
- Allocate, map, read, readahead, copy, and remove DA blocks in the data or attr fork.

## Important Functions
- `xfs_da3_split` walks from a leaf back toward the root, splitting leaf or node blocks as necessary and propagating last-hash updates up the path.
- `xfs_da3_root_split` copies the old root to a new block, creates a new root, and installs two child entries pointing at the split children.
- `xfs_da3_node_split`, `xfs_da3_node_rebalance`, and `xfs_da3_node_add` split full intermediate nodes, rebalance entries between siblings, and insert child pointers.
- `xfs_da3_join`, `xfs_da3_root_join`, `xfs_da3_node_toosmall`, and `xfs_da3_node_unbalance` shrink btrees after deletion by coalescing or dropping underfilled blocks.
- `xfs_da3_node_lookup_int` performs the core btree lookup. It descends from `geo->leafblk`, validates each buffer, binary-searches node entries by hash, and handles duplicate hashes by shifting to adjacent leaves when needed.
- `xfs_da3_path_shift` moves an active search path to the next or previous block at the same level by walking up to a parent edge and then back down.
- `xfs_da3_blk_link` and `xfs_da3_blk_unlink` maintain same-level doubly linked lists using the common `xfs_da_blkinfo` prefix.
- `xfs_da_grow_inode_int`, `xfs_da_grow_inode`, `xfs_da_shrink_inode`, and `xfs_da3_swap_lastblock` handle logical file space allocation and deallocation for DA blocks.
- `xfs_dabuf_map`, `xfs_da_get_buf`, `xfs_da_read_buf`, and `xfs_da_reada_buf` map fork offsets to buffer maps and acquire/read/readahead metadata buffers.

## Data and Invariants
- The tree uses hash values as separator keys, with each node entry storing the largest hash under its child in `hashval` and the child logical block in `before`.
- `xfs_da_state.path` tracks the active descent path; `altpath` is used for neighboring blocks during joins; `extrablk` handles double-split attr leaf cases.
- Magic numbers are normalized in state blocks to `XFS_DA_NODE_MAGIC`, `XFS_ATTR_LEAF_MAGIC`, or `XFS_DIR2_LEAFN_MAGIC` so most logic does not need separate v2/v3 cases.
- Node levels must be nonzero for internal nodes, must not exceed `XFS_DA_NODE_MAXDEPTH`, and must decrease consistently while descending.
- Directory data-fork leaf/node blocks are expected in the leaf/free logical space ranges; attr-fork DA blocks use attr geometry and single-fsb block sizing.

## Error Handling and Corruption Response
- Verifier failures return `-EFSCORRUPTED` or `-EFSBADCRC`, mark buffers corrupt, and mark the directory/attribute fork sick through `xfs_da_mark_sick` or `xfs_dirattr_mark_sick`.
- Mapping holes are corruption unless `XFS_DABUF_MAP_HOLE_OK` is supplied.
- `xfs_da_shrink_inode` has special handling for data-fork `-ENOSPC` during unmap: it swaps the target with the last btree block so the final block can be removed without forcing a bmap split.
- Read paths disambiguate attr-fork `-ENODATA` from disk medium failure by converting it to `-EIO`.

## Dependencies
This file is central glue for `xfs_attr_leaf.c`, directory leaf/node code, bmap allocation/unmap APIs, transaction logging, buffer verifiers, health reporting, and tracepoints. It depends heavily on geometry from `xfs_da_geometry`, on on-disk format definitions in `xfs_da_format.h`, and on directory helpers from `xfs_dir2.h`/`xfs_dir2_priv.h`.

## Research Notes
The file is the main place where XFS makes directory and attribute trees share code. The most important behavioral pattern is that all structural edits are transaction-logged at precise byte ranges, while btree separators are repaired by propagating each child block's last hash upward after splits, joins, and shifts.
