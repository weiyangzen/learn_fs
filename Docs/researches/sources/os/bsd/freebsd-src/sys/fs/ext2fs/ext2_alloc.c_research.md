# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_alloc.c

This file implements FreeBSD ext2/ext3/ext4 block and inode allocation, freeing, group accounting, allocation preferences, lazy bitmap/table initialization, and backup-superblock placement logic.

Key responsibilities:
- Allocate file data blocks and external metadata blocks with preferred-block, quadratic rehash, and brute-force group fallback.
- Reallocate clustered indirect-map blocks into contiguous physical ranges when `vfs.ext2fs.doreallocblks` is enabled.
- Allocate vnodes/inodes, pick directory-preferred groups, initialize generation/birth time, and initialize ext4 extent roots when needed.
- Maintain superblock and group descriptor free block/inode/directory counters, including 64-bit group descriptor high fields.
- Validate, initialize, checksum, and update block/inode bitmaps.
- Free blocks and inodes, update cluster summaries, and maintain directory totals.
- Calculate sparse-superblock/meta_bg group descriptor backup block counts.

Important functions:
- `ext2_alloc`: Main block allocator; enforces reserved block policy, calls `ext2_hashalloc`, updates sequential allocation hints and `i_blocks`.
- `ext2_alloc_meta`: Allocates external metadata blocks, used by xattrs and extent index blocks.
- `ext2_reallocblks`: Moves a cluster of logical blocks to a contiguous allocation and rewrites direct/indirect pointers.
- `ext2_valloc`: Allocates an inode and new vnode, initializes extents or block pointers, and inserts into the vnode hash.
- `e2fs_gd_get_*` / setters: Read and write split low/high group descriptor fields.
- `ext2_dirpref`, `ext2_blkpref`, `ext2_hashalloc`: Directory group choice, block preference, and group fallback policy.
- `ext2_cg_block_bitmap_init`, `ext2_alloccg`, `ext2_clusteralloc`, `ext2_nodealloccg`: Bitmap initialization and allocation internals.
- `ext2_blkfree`, `ext2_vfree`, `ext2_cg_has_sb`, `ext2_cg_number_gdb`: Freeing and metadata layout helpers.

Important interactions:
- Uses `ext2_csum.c` for bitmap checksum verification/set operations.
- Called by `ext2_balloc.c`, `ext2_extents.c`, `ext2_inode.c`, extattr code, and directory create paths.
- Uses the ext2 mount mutex around shared accounting, dropping it for bitmap I/O.

Notable risks:
- Several allocation paths return `EFBIG` in callers if a 64-bit allocation cannot fit a 32-bit classic block pointer; callers must free or avoid unusable high blocks.
- Lazy bitmap initialization depends on checksum feature bits and must stay aligned with group descriptor flags.
