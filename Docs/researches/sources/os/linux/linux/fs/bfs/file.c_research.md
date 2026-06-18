# File Research: sources/os/linux/linux/fs/bfs/file.c

## Purpose
Implements BFS regular file operations, page-cache address-space operations, and contiguous block allocation/movement.

## File Operations
- `generic_file_llseek`
- `generic_file_read_iter`
- `generic_file_write_iter`
- `generic_file_mmap_prepare`
- `filemap_splice_read`

## Block Movement
- `bfs_move_block()` reads one old block, copies data into a new block, marks new dirty, and forgets old buffer.
- `bfs_move_blocks()` moves an inclusive range of blocks to a new location.

## Block Mapping and Allocation
- `bfs_get_block()`:
  - maps existing blocks without allocation when `create == 0`
  - grants writes within existing allocation
  - checks filesystem block bounds
  - serializes allocation/movement under global BFS mutex
  - extends files in place if the file is currently the last allocated file
  - otherwise moves the whole file to the next free region after `si_lf_eblk`
  - updates free block count, last-file end block, inode range, and maps the result

## Address-Space Operations
- `bfs_writepages()`: mpage writeback.
- `bfs_read_folio()`: block read into folio.
- `bfs_write_begin()`: block write begin with failure cleanup.
- `bfs_bmap()`: generic block mapping.
- `bfs_aops`: dirty/invalidate/read/write/bmap/migrate hooks.

## Research Notes
BFS uses contiguous file allocation. Extending a non-last file may relocate the entire file, which is simple but expensive and sensitive to allocation accounting. The comment notes an assumption that inode writeback cannot update `inode->i_blocks` during part of allocation accounting.
