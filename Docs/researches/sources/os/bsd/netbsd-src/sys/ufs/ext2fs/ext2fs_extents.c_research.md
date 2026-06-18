# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_extents.c

This file implements read-side ext4 extent lookup and a small extent cache.

Key public functions:
- `ext4_ext_in_cache`: checks the inode extent cache for a logical block.
- `ext4_ext_put_cache`: stores an extent or sparse gap in the inode extent cache.
- `ext4_ext_find_extent`: walks the inode’s extent tree to locate the extent or sparse range covering a logical block.

Key internal functions:
- `ext4_ext_binsearch_index`: binary-searches an index node and detects sparse ranges before the first indexed block.
- `ext4_ext_binsearch`: binary-searches a leaf extent list and detects sparse gaps before, between, or after extents.

Important behavior:
- The root extent header is stored in the inode’s `e2di_blocks` array.
- Interior nodes are read from disk using index entries’ physical block references.
- `struct ext4_extent_path` carries the current buffer, header, selected index/extent, and sparse result.
- Sparse ranges are represented as synthetic extents with zero physical start and `ep_is_sparse = true`.

Dependencies:
- Ext2fs and UFS inode/buffer APIs.
- `ext2fs_extents.h` for extent structures.
- `bread`/`brelse` for reading extent tree blocks.

Design notes:
- This is lookup support only; there is no extent allocation, insertion, or deletion here.
- Callers must release `path->ep_bp` if non-null.
