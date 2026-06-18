# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/punch.c

Implements block deallocation for inode logical ranges through `ext2fs_punch()`. It supports inline data, extent-based files, and traditional direct/indirect block maps.

The indirect path recursively walks direct, indirect, double-indirect, and triple-indirect pointers, clears entries in the punched range, frees now-empty indirect blocks, and subtracts freed blocks from `i_blocks`.

The extent path opens the extent tree, edits extents around the punched range, splits extents when the punched range is in the middle, deletes empty extents, fixes parent indexes, and frees physical blocks. Bigalloc filesystems use cluster-aware checks before freeing boundary clusters.

Inline data punching clears inline payload and removes inline-data extended attributes only when the punch starts at logical block zero. The final inode is written after successful deallocation.
