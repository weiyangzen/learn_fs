# File Research: sources/local-fs/xfsprogs/libxfs/xfs_da_btree.c

## Purpose

`xfs_da_btree.c` implements the shared directory/attribute B-tree engine for libxfs. It manages dir/attr state objects, da node verification, buffer mapping, tree lookup, node/leaf split and join propagation, sibling link maintenance, directory/attribute block allocation, and hash-name comparison.

## Main Behavior

The file normalizes v2/v3 da node headers with `xfs_da3_node_hdr_from_disk` and `xfs_da3_node_hdr_to_disk`, verifies CRC-enabled metadata fields, and provides read/write buffer ops that can redirect leaf-level blocks to attr or directory leaf verifiers when a node read lands on a leaf. `xfs_da3_header_check` dispatches owner/header checks for attr leaves, da nodes, and directory leaf blocks.

Tree growth centers on `xfs_da3_split`. It walks upward from a split attr or dir leaf, inserts the new child into parent nodes, splits full intermediate nodes, handles attr double-split extra blocks, updates parent hash values, and calls `xfs_da3_root_split` when the root must grow. Root splitting copies the old root to a newly allocated block and creates a fresh root containing two child pointers.

Tree shrinking centers on `xfs_da3_join`. It walks upward from a too-small or empty leaf/node, coalesces with siblings when possible, unlinks and frees dropped blocks, repairs hash paths, and collapses a single-child root through `xfs_da3_root_join`. Node helpers rebalance entries, remove entries, unbalance into a surviving sibling, and keep the last hash value propagated up the path.

Lookup is performed by `xfs_da3_node_lookup_int`, which descends from the root using binary search over node hash entries, validates tree level consistency and owner metadata, handles duplicate hashes, and delegates final leaf lookup to attr or dir leaf code. If a leaf ends at the searched hash and the item is not found, it shifts to the next leaf with `xfs_da3_path_shift` to continue duplicate-hash search.

The allocation layer maps logical da blocks through the inode fork, rejects holes or delayed mappings unless explicitly allowed, and provides get/read/readahead helpers. `xfs_da_grow_inode_int` allocates new metadata blocks, falling back from contiguous to fragmented mappings when needed. `xfs_da_shrink_inode` unmaps dead blocks; for directory data fork ENOSPC cases, `xfs_da3_swap_lastblock` moves the last da block into the removed block’s position and repairs siblings and parent pointers.

## Dependencies and Risks

This file is tightly coupled to bmap mapping/unmapping, transaction logging, buffer verification, attr leaf code, dir leaf code, inode fork geometry, health marking, and the on-disk format definitions in `xfs_da_format.h`. High-risk areas are duplicate-hash traversal, root split/join copy semantics, sibling pointer updates, parent hash repair, owner/CRC verifier dispatch, ENOSPC block swapping, and any mismatch between logical da block numbers and physical buffer mappings.
