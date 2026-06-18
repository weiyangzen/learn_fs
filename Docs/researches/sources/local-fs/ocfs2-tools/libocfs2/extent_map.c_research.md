# File Research: sources/local-fs/ocfs2-tools/libocfs2/extent_map.c

Purpose: maps logical clusters/blocks to physical clusters/blocks by walking extent lists.

Key responsibilities:
- Finds extent records covering a logical cluster.
- Computes hole sizes between records and across adjacent leaf extent blocks.
- Resolves regular inode extent trees and xattr extent trees.
- Converts cluster mappings into block mappings.
- Finds the last allocated logical cluster offset.

Important APIs:
- `ocfs2_get_clusters()`
- `ocfs2_xattr_get_clusters()`
- `ocfs2_extent_map_get_blocks()`
- `ocfs2_get_last_cluster_offset()`

Core invariants:
- Leaf extent lists must have `l_tree_depth == 0` after path descent.
- A physical cluster value of `0` indicates a hole to callers.
- Hole length is returned as clusters until the next allocated extent or `UINT32_MAX - v_cluster` at EOF-like tail.
- Block mapping adds the block offset within the cluster to the resolved physical cluster start.
- `ret_count` is returned in blocks and adjusted for intra-cluster offset.

Dependencies:
- Uses `ocfs2_find_leaf()`, `ocfs2_tree_find_leaf()`, `ocfs2_search_extent_list()`, and extent block I/O.
- Depends on conversion helpers for clusters and blocks.

Notable behavior:
- Despite the file name, the implementation does not maintain a persistent in-memory rbtree cache here; it resolves from on-disk/cached extent lists on demand.
- `ocfs2_xattr_get_clusters()` returns `-1` for a hole rather than returning a normal `0` plus `p_cluster == 0`, unlike `ocfs2_get_clusters()`.
