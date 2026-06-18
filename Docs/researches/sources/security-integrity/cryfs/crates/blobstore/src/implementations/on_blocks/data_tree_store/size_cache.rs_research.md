# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/size_cache.rs

Purpose: implements `SizeCache`, the lazy cache for a `DataTree`'s number of leaves and total byte count. It uses the tree invariant that all leaves except the rightmost are full, so total bytes can be derived from leaf count plus rightmost leaf size.

Important APIs and types: `SizeCache` has states `SizeUnknown`, `RootIsInnerNodeAndNumLeavesIsKnown { num_leaves, rightmost_leaf_id }`, and `NumBytesIsKnown { num_leaves, rightmost_leaf_num_bytes }`. Main methods are `get_or_calculate_num_leaves`, `get_or_calculate_num_bytes`, `update`, and `_calculate_leaf_size`. Helper `NumLeavesAndRightmostLeafId` and recursive `calculate_num_leaves_and_rightmost_leaf_id` find the right border of an inner-rooted tree.

Control flow: leaf-rooted unknown caches immediately become `NumBytesIsKnown` with one leaf. Inner-rooted unknown caches traverse down the last child chain; for each inner level, all left siblings are assumed full and counted via `layout.num_leaves_per_full_subtree(depth - 1)`, while the last child is loaded recursively until the rightmost leaf ID is found. Byte calculation may then load that rightmost leaf to read its actual size. `update` is called after write/resize operations with authoritative leaf count and byte count, deriving the rightmost leaf size by subtracting full left leaves.

State and persistence behavior: cache state is in-memory only and lives inside `DataTree`. It stores a block ID when only leaf count is known to avoid loading the rightmost leaf until total bytes are requested. A comment notes a deadlock risk if a leaf root were stored as `rightmost_leaf_id` and then loaded while already borrowed, so leaf roots cache byte size directly.

Dependencies and integration points: called by `DataTree::num_bytes`, `num_nodes`, `_traverse_leaves_by_byte_indices`, and `resize_num_bytes`. It depends on `DataNodeStore` loading, `NodeLayout` capacity math, `BlockId`, and `NonZeroU64`.

Risks: correctness depends on the tree being left-packed and all non-rightmost leaves being full. Corrupt depth metadata, missing children, or a leaf where an inner node is expected produce errors. `update` unwraps conversion of computed rightmost size to `u32`; this is safe if layout limits are honored but would panic on violated invariants. The file itself has TODOs for tests.

Test signals: no direct tests in this file. Indirect coverage comes from `DataTree` tests that compare cached and recalculated `num_bytes`/`num_nodes`, write growth, resize shrink/growth, and reload after cache clearing.
