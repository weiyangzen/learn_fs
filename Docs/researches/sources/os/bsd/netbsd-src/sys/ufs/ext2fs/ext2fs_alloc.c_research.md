# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_alloc.c

This file implements ext2fs block and inode allocation/freeing, bitmap updates, group descriptor counter maintenance, group descriptor checksum handling, and lazy initialization of ext4 uninitialized bitmaps/inode tables.

Key public functions:
- `ext2fs_alloc`: allocates a data block, respecting reserved-space policy and preferred block selection.
- `ext2fs_valloc`: allocates an inode, choosing directory placement via `ext2fs_dirpref`.
- `ext2fs_blkpref`: chooses a preferred block for locality/contiguity.
- `ext2fs_blkfree`: frees a block and updates bitmap/group counters.
- `ext2fs_vfree`: frees an inode and updates bitmap/group counters.
- `ext2fs_cg_verify_and_initialize`: verifies group descriptor checksums and zeroes uninitialized inode-table ranges when mounting read-write.

Key internal functions:
- `ext2fs_hashalloc`: preferred group, quadratic rehash, then brute-force allocator search.
- `ext2fs_alloccg`: allocates a block from a specific cylinder group bitmap.
- `ext2fs_nodealloccg`: allocates an inode from a specific inode bitmap.
- `ext2fs_mapsearch`: finds a free bit in a block bitmap.
- `ext2fs_cg_update`: updates low/high free block, free inode, directory counts, inode-table-unused, and group descriptor checksum.
- `ext2fs_cg_get_csum`: computes ext4 metadata checksum or legacy group descriptor checksum.
- `ext2fs_init_bb`: initializes an uninitialized block bitmap.

Dependencies:
- NetBSD vnode/buffer APIs: `bread`, `bdwrite`, `getblk`, `clrbuf`.
- UFS inode and mount structures.
- `crc16` and an in-file CRC32C table for ext4 metadata checksums.
- Ext2fs superblock and group descriptor macros from `ext2fs.h`.

Important behavior:
- Allocation decrements global and group free counters and marks the superblock modified.
- Freeing validates range/duplicate-free conditions; duplicate free of a block panics.
- Lazy ext4 group initialization is supported for block and inode bitmaps and inode tables when descriptor checksum features are present.
- Directory inode placement chooses groups with above-average free inodes and high free block count.

Notable implementation risks:
- The checksum path is sensitive because descriptor data must be in little-endian disk encoding when checksummed.
- Error returns from bitmap reads often degrade to allocation failure instead of surfacing the exact I/O error.
