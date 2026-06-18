# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_fs.c

Filesystem core layer tying the superblock, feature checks, group descriptors, bitmap/table initialization, inode references, inode allocation/freeing, truncation, and logical-to-physical block mapping together.

Key behavior:
- `ext4_fs_init` reads and validates the superblock, checks supported features, computes indirect block limits, marks writable filesystems dirty/error-state on mount, increments mount count, and seeds UUID CRC32C.
- `ext4_fs_fini` marks the filesystem clean/valid on writable unmount and writes the superblock.
- Feature check helpers log compatible, incompatible, and read-only-compatible feature bits; unsupported incompatible features fail, unsupported RO-compatible features force read-only.
- Lazy group initialization routines create block bitmaps, inode bitmaps, and inode tables for groups marked uninitialized.
- Group descriptor handling locates descriptor blocks across normal/meta_bg layouts, verifies checksums, initializes uninit groups, and recomputes checksums on dirty put.
- Inode reference handling maps inode numbers to inode table blocks, verifies inode checksums, and writes updated checksums/dirty inode table blocks.
- `ext4_fs_alloc_inode` allocates through `ext4_ialloc`, zeroes and initializes inode fields, permissions, mode, timestamps, extra inode size, and block arrays.
- `ext4_fs_free_inode` frees indirect metadata blocks, extended attribute blocks, and the inode allocation bit; extent data is expected to have been removed by truncation first.
- `ext4_fs_truncate_inode` shrinks files/directories/symlinks/devices and dispatches either extent range removal or indirect-block release.
- `ext4_fs_get_inode_dblk_idx_internal`, `ext4_fs_init_inode_dblk_idx`, and `ext4_fs_append_inode_dblk` provide block mapping/allocation for both extent and legacy direct/indirect files.
- Link count helpers implement special directory link count behavior for indexed directories and `DIR_NLINK`.

Notable dependencies:
- Superblock and descriptor field helpers from `ext4_super`, `ext4_block_group`, and `ext4_inode`.
- Allocation via `ext4_balloc` and `ext4_ialloc`.
- Extent mapping via `ext4_extent`.
- Checksums via `ext4_crc32` and `ext4_block_group`.

Research notes:
- `ext4_fs_init` marks writable filesystems as error-state before full operation and `ext4_fs_fini` marks valid on unmount, mirroring ext-style dirty mount semantics.
- `support_unwritten` is accepted in block mapping wrappers but is not materially used in this implementation path.
- Extent append grows inode size immediately after allocating one mapped block.
- Indirect block allocation is careful to zero new indirect blocks before linking/using them, but if some mid-path allocations fail after linking parent state, rollback is limited.
- `ext4_fs_inode_to_goal_block` returns an inode’s block group number, not an actual block address; callers should treat it only as a coarse hint.
