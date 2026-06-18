# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_balloc.c

Ext4 block allocation and freeing implementation. It maps block addresses to block groups, verifies and updates block bitmap checksums, allocates physical blocks near a goal, frees individual or ranged blocks, and updates superblock, block group, inode block counts, transaction revocation, and cache invalidation.

Key behavior:
- `ext4_balloc_get_bgid_of_block` and `ext4_balloc_get_block_of_bgid` convert between absolute block addresses and block group numbers, accounting for `first_data_block`.
- Metadata checksum support computes block bitmap CRC32C from the filesystem UUID seed and bitmap contents.
- `ext4_balloc_free_block` and `ext4_balloc_free_blocks` clear bitmap bits, update free counts and inode block counts, mark group descriptors dirty, revoke blocks from the transaction layer, and invalidate cache lines for freed LBAs.
- `ext4_balloc_alloc_block` first tries the requested goal, then nearby bits within the same group, then the rest of the group, then later block groups modulo the group count.
- `ext4_balloc_try_alloc_block` conditionally allocates a specific physical block and reports whether it was free.

Notable dependencies:
- Bitmap helpers from `ext4_bitmap.c`.
- Group descriptors via `ext4_block_group` and `ext4_fs`.
- Checksums via `ext4_crc32`.
- Transaction/cache interactions through `ext4_trans` and `ext4_bcache`.

Research notes:
- Bitmap checksum mismatches are warnings in most allocation/free paths; operations continue after logging rather than failing hard.
- Freeing range logic handles group crossing and warns if non-flex-bg continuous ranges cross block groups.
- Count updates are manual and distributed across superblock, block group descriptor, and inode fields; callers rely on these to keep allocation statistics coherent.
- The allocator is simple first-fit around a goal, not a locality-aware multi-block allocator comparable to Linux mballoc.
