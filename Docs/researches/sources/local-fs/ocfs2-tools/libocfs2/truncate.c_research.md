# File Research: sources/local-fs/ocfs2-tools/libocfs2/truncate.c

Implements userspace OCFS2 truncate operations for regular file data, inline data, xattr value trees, xattr index trees, and indexed directory trees.

Key responsibilities:
- Walks extent trees depth-first and removes extents beyond a requested new size.
- Frees ordinary clusters or decreases refcounts for refcounted extents.
- Zeroes the tail inside a still-allocated cluster after truncation.
- Handles inline data and fast symlink truncation.
- Clears DIO orphan state by forcing truncation to current inode size.

Important functions:
- `truncate_iterate()`: extent iterator callback that trims records, deletes empty extent blocks, and frees clusters.
- `ocfs2_zero_tail_for_truncate()`: zeroes bytes after `new_i_size` inside the remaining cluster, performing COW first if refcounted.
- `ocfs2_zero_tail_and_truncate()`: public helper for trimming extents and zeroing the tail.
- `ocfs2_truncate_inline()`: truncates inline-data files and fast symlinks.
- `ocfs2_truncate_full()` / `ocfs2_truncate()`: public truncate API.
- `ocfs2_xattr_value_truncate()`, `ocfs2_xattr_tree_truncate()`, `ocfs2_dir_indexed_tree_truncate()`: truncate specialized metadata extent trees.

Dependencies:
- Extent iteration APIs, `ocfs2_free_clusters`, `ocfs2_decrease_refcount`, `ocfs2_refcount_cow`.
- Cached inode APIs and `ocfs2_write_cached_inode`.
- `ocfs2_extent_map_get_blocks` for locating physical blocks.

Research notes:
- Truncating into an internal extent block may require rereading the block to determine whether it became empty.
- If truncation reaches zero clusters, inode tree depth is reset to zero.
- Refcount tree is detached when a refcounted file is truncated to zero.
