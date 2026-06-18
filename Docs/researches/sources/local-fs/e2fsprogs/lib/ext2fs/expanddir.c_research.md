# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/expanddir.c

Implements `ext2fs_expand_dir`, which grows a directory by one block. It uses block iteration in append mode to find or create a hole, allocate a new block, initialize it, update inode size, and update block counts.

Callback behavior in `expand_dir_proc`:
- Existing blocks update the allocation goal.
- Empty block slots allocate a new block near the goal, respecting bigalloc cluster placement when possible.
- For logical block zero, it zeroes the new block.
- For later blocks, it creates a new empty directory block with `ext2fs_new_dir_block` and writes it with `ext2fs_write_dir_block4`.
- Marks block allocation stats and returns `BLOCK_CHANGED`, aborting once a usable directory block is added.

Top-level validation:
- Requires a read-write filesystem.
- Requires a block bitmap.
- Verifies the inode is a directory.
- Handles inline-data directories by delegating to `ext2fs_inline_data_expand`.

Post-update behavior:
- Re-reads the inode.
- Increases inode size by one filesystem block via `ext2fs_inode_size_set`.
- Adds allocated block count with `ext2fs_iblk_add_blocks`.
- Writes the inode.

Implementation notes:
- `es.newblocks` tracks newly allocated clusters/blocks for inode accounting.
- If append iteration does not add a directory block, returns `EXT2_ET_EXPAND_DIR_ERR`.
