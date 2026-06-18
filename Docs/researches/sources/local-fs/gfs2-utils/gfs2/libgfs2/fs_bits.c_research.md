# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/fs_bits.c

This file implements GFS2 allocation bitmap search and block-state get/set helpers.

Public APIs:
- `lgfs2_blkst_str()`: maps bitmap state constants to names.
- `lgfs2_bitfit()`: finds the next block with a requested two-bit bitmap state.
- `lgfs2_check_range()`: validates a filesystem block number against superblock limits.
- `lgfs2_set_bitmap()`: updates an rgrp bitmap entry and marks the bitmap dirty.
- `lgfs2_get_bitmap()`: reads a block state from a resource group bitmap.

Important behavior:
- `lgfs2_bitfit()` scans 64 bits at a time using two-bit state matching.
- Bitmap entries encode four block states: free, used, unlinked, dinode.
- `lgfs2_get_bitmap()` can locate the resource group itself or accept one from the caller.
- First bitmap block has a different metadata header size than later bitmap blocks; offset calculations account for that.

Integration role:
- Used by block allocation, resource-group scanning, grow, mkfs, and directory/file allocation flows.

Risk notes:
- Bitmap math is dense and relies on correct `rt_bits`, `bi_start`, `bi_len`, `bi_offset`, and `sd_blocks_per_bitmap`.
- Range check treats blocks at or below the superblock address as invalid.
- `lgfs2_get_bitmap()` returns free for an unloaded `bi_data`, which callers must understand.
