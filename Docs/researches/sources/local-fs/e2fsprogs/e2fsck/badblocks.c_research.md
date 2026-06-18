# File Research: sources/local-fs/e2fsprogs/e2fsck/badblocks.c

## Purpose
Maintains the ext filesystem bad-block inode from either a supplied bad-block list file or the external `badblocks` scanner.

## Main Flow
`read_bad_blocks_file()`:
- Ensures bitmaps are loaded.
- Scans the bad-block inode and clears illegal existing block references.
- If appending, reads the current bad-block inode into a `badblocks_list`.
- If a file is supplied, opens it; otherwise runs `badblocks -b <blocksize> -X ... <device> <last_block>` via `popen`.
- Reads bad blocks with `ext2fs_read_bb_FILE()`.
- Updates the bad-block inode through `ext2fs_update_bb_inode()`.

## Validation
`check_bb_inode_blocks()` rejects block numbers below `s_first_data_block` or beyond filesystem block count, clears the invalid pointer, and returns `BLOCK_CHANGED`.

## Integration
Used by e2fsck command-line bad block options (`-c`, `-l`, `-L`) through the declaration in `e2fsck.h`.

## Risks / Notes
- The `badblocks` command string is assembled with `sprintf` into a 1024-byte buffer; device names are normally controlled by CLI input.
- On fatal errors it sets `E2F_FLAG_ABORT`.
