# File Research: sources/teaching/minix/minix/fs/mfs/stats.c

`stats.c` provides `count_free_bits`, a bitmap scanner used for mount-time block usage and statvfs inode/free-space reporting. It supports both inode and zone maps, deriving the start block, number of valid bits, number of bitmap blocks, and starting origin from the superblock.

The scanner walks bitmap blocks and chunks, byte-swapping each chunk with `conv4` when needed, counts zero bits within the valid map range, and stops at the end of the map. It uses `get_block` for bitmap blocks and releases each buffer after scanning.

Despite the stale comment saying "Allocate a bit", the routine is read-only accounting and does not modify bitmap state.
