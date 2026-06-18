# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_htree.c

This file implements ext3/ext4 HTree indexed directory lookup, index creation, and indexed directory insertion.

Key responsibilities:
- Detect HTree-indexed directories.
- Traverse one- or two-level HTree indexes to find target leaf directory blocks.
- Handle hash collisions by checking adjacent leaves when required.
- Search leaf directory blocks with the normal ext2 directory scanner.
- Convert a linear directory block into indexed root plus leaf blocks.
- Split full directory blocks by hash order and insert the new entry into the correct half.
- Split full index nodes or create a second HTree level.
- Maintain directory and htree checksums when metadata checksums are enabled.

Important functions:
- `ext2_htree_has_idx`: Checks feature and inode flag.
- `ext2_htree_find_leaf`: Reads root, validates hash version/limits, computes hash, and walks index levels.
- `ext2_htree_lookup`: Searches selected and collision-adjacent leaf blocks.
- `ext2_htree_create_index`: Converts a directory to HTree format and appends two leaf blocks.
- `ext2_htree_add_entry`: Splits full leaves and indexes, appends new blocks, and writes updated index buffers.
- `ext2_htree_split_dirblock`: Sorts entries by hash, moves roughly half to a new block, and computes split hash.
- `ext2_htree_insert_entry`, `ext2_htree_writebuf`, `ext2_htree_check_next`: Index manipulation and write helpers.

Important interactions:
- Uses `ext2_htree_hash` from `ext2_hash.c`, directory structures from `ext2_dir.h`, and checksum functions from `ext2_csum.c`.
- Calls `ext2_blkatoff`, `ext2_search_dirblock`, `ext2_add_entry`, `VOP_WRITE`, and buffer-cache writes.

Notable risks:
- Lookup intentionally avoids `.` and `..`.
- Directory index depth is limited to at most one indirect level beyond the root in this implementation.
