# File Research: sources/local-fs/ocfs2-tools/libocfs2/extent_tree.c

Purpose: generic OCFS2 extent-tree mutation engine for userspace tools.

Key responsibilities:
- Provides a common extent-tree abstraction for dinodes, refcount blocks, xattr values, and indexed-directory dx roots.
- Finds paths through extent btrees.
- Inserts extents, including contiguous coalescing, tail append, branch growth, tree-depth growth, and leaf rotations.
- Splits extent records for flag changes or interior removals.
- Clears/sets extent flags while preserving allocation.
- Removes extents and shrinks/rotates trees after deletion.
- Duplicates extent-block trees before mutation to improve write ordering and rollback behavior.

Important public APIs:
- `ocfs2_init_dinode_extent_tree()`
- `ocfs2_init_refcount_extent_tree()`
- `ocfs2_init_xattr_value_extent_tree()`
- `ocfs2_init_dx_root_extent_tree()`
- `ocfs2_search_extent_list()`
- `ocfs2_new_path_from_et()`, `ocfs2_find_path()`, `ocfs2_free_path()`
- `ocfs2_tree_insert_extent()`
- `ocfs2_change_extent_flag()`
- `ocfs2_remove_extent()`
- `ocfs2_tree_find_leaf()`, `ocfs2_find_leaf()`

Extent-tree abstraction:
- `ocfs2_extent_tree_operations` supplies root extent-list lookup, last extent-block getter/setter, cluster-count updates, optional sanity check, optional max leaf cluster fill, and optional contiguity logic.
- Dinode trees update `i_last_eb_blk` and `i_clusters`.
- Refcount trees update `rf_last_eb_blk` and `rf_clusters`, and intentionally report no normal extent contiguity.
- Xattr value trees update `xr_last_eb_blk` and `xr_clusters`.
- Dx root trees update `dr_last_eb_blk` and `dr_clusters`.

Core insertion flow:
- `ocfs2_tree_insert_extent()` builds an `insert_ctxt`, optionally duplicates existing extent blocks, computes insert type, grows the tree if no free record is available, performs insertion, frees old or duplicate blocks based on success, and writes the root buffer.
- Insert type classification detects split, append, contiguous, tree depth, and free-record state.
- Contiguous inserts merge only when flags match.
- Non-contiguous inserts can rotate records right from the rightmost leaf to create a free slot near the target.
- If no leaf has space, the code either adds a branch at a lower non-leaf target or shifts root depth and creates new extent blocks.

Tree-shape mechanics:
- Paths are represented by `struct ocfs2_path`, with root at index 0 and leaf at `p_tree_depth`.
- `ocfs2_add_branch()` allocates a chain of empty extent blocks, links the previous last leaf through `h_next_leaf_blk`, and updates the owner’s last extent block.
- `shift_tree_depth()` copies root records into a new extent block, turns the root into an internal node, and updates last leaf for depth 1.
- Left and right rotations maintain parent `e_cpos` and `e_int_clusters` through `ocfs2_complete_edge_insert()` and related edge-length helpers.
- Empty extents are treated specially and must live at index 0 of a leaf.

Flag-change and split behavior:
- `ocfs2_change_extent_flag()` locates the containing extent, validates requested set/clear state, builds a replacement record with changed flags and requested physical start, then calls split/merge logic.
- `ocfs2_split_extent()` handles full-cover replacement, edge splits, middle splits, and merges with adjacent compatible records.
- Middle splits are modeled as a right split followed by a second left-side pass.

Removal behavior:
- `ocfs2_remove_extent()` handles full record removal, edge truncation, and middle removal.
- Middle removal first splits the right side, then re-finds the left part and truncates.
- `ocfs2_rotate_tree_left()` removes empty slots after deletion and can delete the rightmost path or collapse the tree back to root-inline extents.

Write-ordering behavior:
- For trees with external extent blocks, insertion and flag changes attempt to duplicate the existing extent-block tree.
- On success, mutation happens in duplicate blocks and old blocks are freed.
- On failure after duplication, duplicate blocks are freed and the original root copy is restored.
- If duplication fails, the code falls back to normal in-place mutation.

Notable risks:
- Many internal helpers use `assert()` for structural assumptions; malformed images in non-assert builds still rely on surrounding corruption checks.
- Several functions return plain `int` while carrying `errcode_t` values.
- The mutation logic is complex and highly invariant-dependent: empty extent position, correct `h_next_leaf_blk`, correct `last_eb_blk`, and parent length updates are all essential.
