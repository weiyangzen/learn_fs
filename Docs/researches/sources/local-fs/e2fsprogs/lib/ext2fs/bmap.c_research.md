# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bmap.c

Maps a logical file block to a physical filesystem block and optionally allocates, sets, or zeroes the mapping. The primary API is `ext2fs_bmap2`; `ext2fs_bmap` is the legacy 32-bit wrapper.

Classic block mapping:
- Direct blocks are read or updated from `inode->i_block`.
- Single, double, and triple indirect mappings use `block_ind_bmap`, `block_dind_bmap`, and `block_tind_bmap`.
- Missing indirect blocks can be allocated when `BMAP_ALLOC` is set.
- `BMAP_SET` writes a caller-provided physical block and errors if the required indirect block is absent.
- Big-endian builds swap indirect block entries on read/write.

Extent mapping:
- Extent inodes are handled by `extent_bmap`.
- Existing extents are found through `ext2fs_extent_goto` and `EXT2_EXTENT_CURRENT`.
- `BMAP_ALLOC` can allocate a new block and install it with `ext2fs_extent_set_bmap`.
- `BMAP_UNINIT` preserves uninitialized extent state.
- `BMAP_RET_UNINIT` is returned through `ret_flags`.

Bigalloc behavior:
- `implied_cluster_alloc` maps unallocated logical blocks to an already allocated physical cluster sibling.
- `ext2fs_map_cluster_block` exposes cluster-relative lookup for bigalloc extent files.

Validation and updates:
- `ext2fs_file_block_offset_too_big` rejects offsets past classic indirect addressing limits or the kernel 32-bit logical block cutoff.
- Inline-data inodes return `EXT2_ET_INLINE_DATA_NO_BLOCK`.
- Allocations update inode block counts via `ext2fs_iblk_add_blocks` and write the inode.
- `BMAP_ZERO` zeroes the mapped physical block after successful lookup/allocation.

Implementation notes:
- The function can read the inode itself if the caller passes NULL.
- It allocates two block buffers when none is supplied.
- Legacy `ext2fs_bmap` returns `EOVERFLOW` if the resulting physical block does not fit in 32 bits.
