# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/write_bb_file.c

## Purpose
Writes an ext2 bad-block list to a `FILE *`.

## Main Behavior
- Starts a badblocks iterator with `ext2fs_badblocks_list_iterate_begin()`.
- Prints each block number as an unsigned decimal line.
- Ends the iterator and returns success.

## Integration
Provides `ext2fs_write_bb_FILE()`, matching the plain text format consumed by e2fsprogs bad-block list readers.

## Risks / Notes
Uses legacy `blk_t` and `%u`, so it is tied to the classic 32-bit badblocks-list format.
