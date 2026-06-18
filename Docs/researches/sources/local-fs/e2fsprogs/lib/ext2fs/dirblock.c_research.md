# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dirblock.c

Provides directory block read/write wrappers with checksum verification/set and endian swapping. The primary APIs are `ext2fs_read_dir_block4` and `ext2fs_write_dir_block4`; older 3/2/no-suffix variants wrap them.

Read behavior:
- Reads one block via `io_channel_read_blk64`.
- Verifies directory block checksum unless `EXT2_FLAG_IGNORE_CSUM_ERRORS` is set.
- On big-endian builds, swabs directory entries into host order.
- Returns `EXT2_ET_DIR_CSUM_INVALID` if checksum verification failed and no read/swap error occurred.

Write behavior:
- On big-endian builds, copies the input buffer and swabs directory entries out.
- Sets directory block checksum with `ext2fs_dir_block_csum_set`.
- Writes one block via `io_channel_write_blk64`.

Implementation notes:
- The 3/2/legacy variants pass inode zero, which limits checksum contexts for callers that do not know the inode.
- Big-endian error paths rely on freeing the temporary buffer after checksum/write handling.
