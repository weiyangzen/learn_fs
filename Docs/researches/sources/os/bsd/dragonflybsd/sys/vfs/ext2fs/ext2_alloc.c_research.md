# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_alloc.c

This file implements ext2 block and inode allocation/freeing for DragonFlyBSD, including group selection, bitmap updates, cluster accounting, lazy bitmap/table initialization, group descriptor counters, and sparse-superblock metadata layout helpers.

Key responsibilities:
- Allocate data blocks and metadata blocks with preferred-block and cylinder-group fallback policy.
- Allocate inodes, choose directory-preferred groups, initialize new vnode/inode state, and seed generation/birth time.
- Reallocate buffered clusters into contiguous disk ranges when `doreallocblks` is enabled.
- Maintain free block/inode counters in the superblock and group descriptors, including 64-bit descriptor fields.
- Initialize uninitialized ext4-style block/inode bitmaps and zero unused inode-table blocks.
- Verify/set block and inode bitmap checksums through `ext2_csum.c`.
- Free blocks and inodes, update directory counts, and maintain cluster summaries.

Important functions:
- `ext2_alloc`: Main block allocator. Checks reserved block limits, chooses a starting group, calls `ext2_hashalloc`, updates sequential allocation hints and `i_blocks`.
- `ext2_alloc_meta`: Allocates an extended-attribute metadata block near the inode.
- `ext2_reallocblks`: Attempts cluster relocation for contiguous allocation; rewrites inode/indirect block pointers, then frees old blocks.
- `ext2_valloc`: Allocates an inode from a preferred group, creates/initializes a vnode, initializes extent trees when enabled, and returns the locked vnode.
- `e2fs_gd_get_*` / `e2fs_gd_set_*`: Access low/high group descriptor fields for bitmaps, inode tables, free counters, directory counts, and unused inodes.
- `ext2_dirpref`: Chooses a directory inode group using average free inodes/blocks, directory density, root-directory spreading, and `e2fs_contigdirs`.
- `ext2_blkpref`: Computes preferred physical block from sequential hints, earlier block map entries, or inode group locality.
- `ext2_hashalloc`: Implements preferred group, quadratic rehash, then brute-force group search.
- `ext2_cg_number_gdb` and helpers: Count group descriptor backup blocks for normal, sparse, sparse-super2, and meta_bg layouts.
- `ext2_alloccg`: Reads and validates a block bitmap, initializes/checksums it when needed, allocates a preferred block or free run, and updates counters.
- `ext2_clusteralloc`: Allocates a contiguous run using cluster summary hints.
- `ext2_nodealloccg`: Reads and verifies an inode bitmap, handles uninitialized inode bitmaps/tables, allocates an inode, and updates counters/checksums.
- `ext2_blkfree` / `ext2_vfree`: Free a block or inode and update bitmaps, counters, checksums, and directory totals.
- `ext2_cg_has_sb`: Implements ext backup-superblock group selection.

Important interactions:
- Relies on `ext2_csum.c` for bitmap checksum verification and updates.
- Uses `ext2_alloc_vnode`, `ext2_vinit`, and `ext4_ext_tree_init` when allocating new inodes.
- Called by `ext2_balloc.c`, truncation paths in `ext2_inode.c`, and directory/vnode creation code.
- Requires the ext2 mount mutex for shared superblock/group accounting but drops it around blocking bitmap I/O.

Notable behavior and risks:
- `ext2_alloc` unlocks the mount mutex on ENOSPC paths, matching callers that enter with the lock held.
- New block numbers above `UINT_MAX` are rejected by indirect-block callers, since classic block maps are 32-bit.
- Lazy bitmap and inode-table initialization is tied to checksum-capable features.
- `ext2_clusteralloc` updates one bitmap bit per `e2fs_fpb`, which reflects the inherited fragment/block accounting assumptions.
