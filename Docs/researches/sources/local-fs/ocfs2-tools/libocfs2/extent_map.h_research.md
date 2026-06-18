# File Research: sources/local-fs/ocfs2-tools/libocfs2/extent_map.h

Purpose: declares internal extent-map data structures.

Key contents:
- Includes `ocfs2/kernel-rbtree.h`.
- Defines `ocfs2_extent_map_entry`.
- Defines `struct _ocfs2_extent_map` with `rb_root em_extents` and `em_clusters`.
- Defines `struct _ocfs2_extent_map_entry` with rb node, tree depth, and one `ocfs2_extent_rec`.

Notable behavior:
- This header describes an rbtree-backed map shape, but the paired `extent_map.c` in this group performs direct extent-tree lookups and does not use these structures.
- The declarations may be legacy, reserved for other compilation units, or retained API surface for future/local cache work.
