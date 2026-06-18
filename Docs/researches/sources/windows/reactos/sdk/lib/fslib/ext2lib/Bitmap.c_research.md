# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Bitmap.c

Read completely: 500 lines.

This file implements ext2 bitmap allocation, bit operations, disk read/write, and cleanup for the ReactOS `mke2fs`-style ext2 library. Low-level helpers `ext2_set_bit`, `ext2_clear_bit`, and `ext2_test_bit` operate on little-endian byte bitmaps. Generic mark/unmark helpers validate the requested bit against bitmap start/end bounds before changing it.

Allocation paths create in-memory block and inode bitmap descriptors from the superblock and group count. Block bitmaps start at `s_first_data_block`, end at `s_blocks_count - 1`, and include `real_end` rounded to the full group layout. Inode bitmaps start at inode 1 and include the full group layout. Allocations use the process heap and zero-fill descriptor and bitmap memory.

Write paths serialize group-sized portions of the in-memory bitmaps to each group's bitmap block. `ext2_write_block_bitmap` fills the output block with `0xff`, copies valid group bitmap bytes, and forces unused padding bits in the last block group to allocated. `ext2_write_inode_bitmap` similarly writes inode bitmap blocks. Optional big-endian bitmap swapping is present behind `EXT2_BIG_ENDIAN_BITMAPS`.

Read paths are consolidated in `read_bitmaps`, which optionally frees existing maps, allocates requested maps, then reads each group bitmap block from disk with `Ext2ReadDisk`; missing bitmap block numbers produce zero-filled group bitmaps. Convenience wrappers read inode, block, or both bitmaps. `ext2_write_bitmaps` writes whichever maps are present.

Important interactions: depends on ext2 superblock/group descriptor macros from `Mke2fs.h`, process heap allocation, and `Ext2ReadDisk`/`Ext2WriteDisk` for block I/O. It is used by formatting and inode/block allocation code to track metadata ownership.

Security/reliability notes: direct bit helpers do not bounds-check; callers must pass valid offsets. Allocation size arithmetic uses 32-bit `ULONG` and assumes sane superblock/group counts. The cleanup path in `read_bitmaps` frees only bitmap descriptors and leaks inner bitmap buffers on partial failure. `ext2_read_bitmaps` returns `0` when both maps already exist, which is `false` despite being a no-work condition; callers need to account for that behavior.
