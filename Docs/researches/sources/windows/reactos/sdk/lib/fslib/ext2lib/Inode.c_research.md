# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Inode.c

This file implements ext2 inode access, block mapping, inode expansion, file data I/O, directory insertion, and reserved-inode accounting.

Core responsibilities:
- `ext2_get_inode_lba`, `ext2_load_inode`, and `ext2_save_inode` map inode numbers to inode table offsets and read/write on-disk inode records.
- `ext2_new_inode` finds a free inode, preferring the parent directory’s group.
- `ext2_expand_inode` and recursive `ext2_expand_block` attach new data blocks through direct, single-indirect, double-indirect, and triple-indirect block pointers.
- `ext2_get_block`, `ext2_block_map`, and `ext2_build_bdl` translate file offsets into disk byte ranges.
- `ext2_read_inode` and `ext2_write_inode` perform file data I/O through block-description lists.
- `ext2_add_entry` inserts an ext2 directory entry into existing directory space.
- `ext2_reserve_inodes` marks reserved inodes between root and first normal inode.

Important behavior:
- `i_blocks` is stored in 512-byte sectors, so the code repeatedly converts with `blocksize / SECTOR_SIZE`.
- Writes allocate enough blocks to cover the requested range, expand inode mapping, update file size, and save the inode.
- Directory insertion splits an existing record when there is spare `rec_len` space.

Risk points:
- `ext2_expand_block` passes `bDirty` as the `newBlk` argument during recursion, which looks suspicious and could corrupt indirect expansion intent.
- `ext2_add_entry` allocates `parent_inode.i_size` bytes but leaks that buffer on several early returns and on successful write.
- Directory free-space checks compare `rec_len >= name_len + rec_len` instead of using rounded current entry length consistently.
- Large-file, sparse-file, and robust error rollback behavior are minimal.
