# File Research: sources/os/linux/linux-stable/fs/bfs/file.c

This file implements BFS regular file operations and block mapping/allocation.

Exports:
- `bfs_file_operations`
- `bfs_aops`
- Empty `bfs_file_inops` declaration/definition.

Main file operations:
- Generic llseek, read_iter, write_iter, mmap prepare, and splice read.

Block allocation:
- `bfs_get_block()` maps logical file blocks to physical BFS blocks.
- Reads map blocks if within `i_eblock`.
- Writes can extend in place if the file is already the last allocated file.
- Otherwise, the entire file is moved to the next free block range after `si_lf_eblk`.
- `bfs_move_block()` copies one block and dirties the destination.
- `bfs_move_blocks()` copies a contiguous file extent block-by-block.

Address-space operations:
- `bfs_writepages()` uses `mpage_writepages()`.
- `bfs_read_folio()` uses `block_read_full_folio()`.
- `bfs_write_begin()` uses `block_write_begin()` and truncates page cache on failure.
- `bfs_bmap()` uses `generic_block_bmap()`.

Integration:
- Uses the global BFS superblock lock for write allocation and movement.
- Updates free block counts and last-file end block.
- Called by BFS VFS file operations and page cache writeback.

Risk notes:
- The allocation strategy is simple and potentially expensive: extending a non-last file moves the entire file.
- A comment notes an assumption that nothing writes the inode back during block allocation while `inode->i_blocks` is being used for free block accounting.
- `bfs_move_block()` uses `bforget()` on the source buffer after copying, which intentionally invalidates the old block mapping.
