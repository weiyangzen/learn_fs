# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_ialloc.c

Inode allocation and freeing logic. It maps inode numbers to block groups, verifies and updates inode bitmap checksums, scans groups for free inodes, and maintains inode counters in group descriptors and the superblock.

Key behavior:
- Converts between absolute inode numbers, per-group inode indexes, and block group IDs.
- Computes inode bitmap CRC32C from the filesystem UUID seed and bitmap contents when `metadata_csum` is enabled.
- `ext4_ialloc_free_inode` clears the inode bitmap bit, updates bitmap checksum, marks the bitmap block and group descriptor dirty, increments free inode counts, decrements used directory counts when applicable, and updates superblock free inode count.
- `ext4_ialloc_alloc_inode` starts searching at `fs->last_inode_bg_id`, wraps once, scans free bits with `ext4_bmap_bit_find_clr`, marks an inode used, updates free/used/unused counters, and records the last successful group.

Notable dependencies:
- Bitmap primitives come from `ext4_bitmap.h`.
- Group descriptor accessors come from `ext4_block_group.h`.
- Metadata checksum support uses `ext4_crc32c`.
- Bitmap blocks are fetched through `ext4_trans_block_get` so journal transactions can capture modifications.

Research notes:
- Inode bitmap checksum mismatches are logged as warnings and allocation/free proceeds.
- Allocation is a simple first-fit group scan, explicitly simpler than Linux's Orlov allocator.
- Error handling in one allocation path calls `ext4_block_set` and then checks the older `rc` value, so a block release error there can be missed.
