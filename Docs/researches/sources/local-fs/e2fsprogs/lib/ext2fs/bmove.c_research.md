# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bmove.c

Implements `ext2fs_move_blocks`, which relocates file blocks away from reserved blocks. It scans all inodes, iterates their blocks, copies block contents to free locations, and updates block pointers through the block iterator callback.

The callback `process_block` checks whether a block is marked in the reserve bitmap. If so, it searches forward, wrapping at filesystem end, for a block absent from both the reserve bitmap and allocation map. It reads the old block, writes it to the new block, updates the block number, marks the allocation map, and returns `BLOCK_CHANGED`.

`EXT2_BMOVE_GET_DBLIST` causes the move pass to rebuild `fs->dblist` by adding directory blocks as they are encountered.

Dependencies: inode scan API, block iterator, block bitmap APIs, IO channel read/write, directory block list APIs.

Implementation notes:
- The provided `alloc_map` defaults to `fs->block_map`.
- It skips unlinked inodes and inodes without valid blocks.
- Error handling stores callback errors in `pb.error` and aborts iteration.
- Several early-return error paths after allocations/scans do not clean up all intermediate resources in this old code path.
