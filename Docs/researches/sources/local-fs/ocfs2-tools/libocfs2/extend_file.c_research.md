# File Research: sources/local-fs/ocfs2-tools/libocfs2/extend_file.c

Purpose: high-level allocation and file-size extension helpers layered over the generic extent tree code.

Key responsibilities:
- Inserts extents into dinode extent trees.
- Allocates clusters and appends them to cached inodes.
- Extends only inode size for already allocated files.
- Allocates unwritten extents over holes for regular files.
- Marks unwritten extents as written by clearing `OCFS2_EXT_UNWRITTEN`.

Important APIs:
- `ocfs2_inode_insert_extent()`
- `ocfs2_cached_inode_insert_extent()`
- `ocfs2_cached_inode_extend_allocation()`
- `ocfs2_extend_allocation()`
- `ocfs2_extend_file()`
- `ocfs2_allocate_unwritten_extents()`
- `ocfs2_mark_extent_written()`

Core invariants:
- Allocation mutations require `OCFS2_FLAG_RW`.
- Unwritten extent allocation requires filesystem support for unwritten extents.
- `ocfs2_allocate_unwritten_extents()` rejects invalid, system, and non-regular inodes.
- Physical cluster allocation is inserted via `ocfs2_tree_insert_extent()` through a dinode extent-tree wrapper.
- If extent insertion fails after cluster allocation, the allocated clusters are freed.

Dependencies:
- Uses cluster allocation/free APIs, cached inode APIs, extent map block lookup, and `extent_tree.c` insertion/flag-change APIs.

Notable behavior and risks:
- `ocfs2_extend_file()` changes `i_size` only; it does not allocate storage.
- `ocfs2_cached_inode_extend_allocation()` bases append `cpos` on rounded-up `i_size`, not necessarily current `i_clusters`.
- `ocfs2_allocate_unwritten_extents()` has early `return` statements after reading `ci` for invalid/system/non-regular cases, which skip cached inode cleanup.
- In the hole lookup loop, `ocfs2_extent_map_get_blocks()` errors cause `continue`, which can risk a non-progress loop if the same mapping error repeats.
