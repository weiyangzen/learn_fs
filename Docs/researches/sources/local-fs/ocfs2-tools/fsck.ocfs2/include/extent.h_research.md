# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/extent.h

Read coverage: complete file read, 71 lines.

Purpose: declares fsck extent-tree validation hooks and state.

Key data:
- `check_leaf_er_func` validates leaf extent records.
- `mark_leaf_er_alloc_func` accounts for leaf extent allocations.
- `struct extent_info` accumulates max byte size, cluster count, last extent block, expected depth, callback pointers, and callback data.

Key API: `o2fsck_check_extents()`, generic `check_el()`, `o2fsck_check_extent_rec()`, and `o2fsck_mark_tree_clusters_allocated()`.

Dependencies: `fsck.h` and OCFS2 extent structures.
