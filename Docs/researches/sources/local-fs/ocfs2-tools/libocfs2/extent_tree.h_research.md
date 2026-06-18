# File Research: sources/local-fs/ocfs2-tools/libocfs2/extent_tree.h

Purpose: internal interface for the generic extent-tree mutation engine.

Key contents:
- Defines `ocfs2_root_write_func`.
- Defines `struct ocfs2_extent_tree`.
- Defines `enum ocfs2_contig_type`.
- Defines `struct ocfs2_extent_tree_operations`.
- Declares extent-tree initializers for dinodes, refcount trees, xattr values, and dx roots.
- Declares insertion, flag-change, and removal APIs.
- Defines `struct ocfs2_path_item`, `struct ocfs2_path`, path macros, and path allocation/search/free APIs.

Core abstractions:
- `ocfs2_extent_tree` binds a root buffer/block, root writer, root extent list, object pointer, operation table, and max leaf cluster setting.
- Operation table separates generic btree algorithms from owner-specific fields such as `i_last_eb_blk`, `rf_last_eb_blk`, `xr_last_eb_blk`, or `dr_last_eb_blk`.
- Path macros expose root and leaf block/buffer/list access.

Notable constraints:
- `OCFS2_MAX_PATH_DEPTH` is 5.
- `eo_set_last_eb_blk`, `eo_get_last_eb_blk`, `eo_update_clusters`, and `eo_fill_root_el` are treated as required by the implementation.
- Optional callbacks allow sanity checks, max leaf cluster filling, and custom contiguity rules.
