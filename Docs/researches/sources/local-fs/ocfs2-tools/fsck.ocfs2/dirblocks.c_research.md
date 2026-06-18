# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/dirblocks.c

Read coverage: complete file read, 260 lines.

Purpose: maintains fsck's in-memory red-black tree of directory data blocks and directory inodes requiring directory-index rebuild.

Behavior:
- `o2fsck_add_dir_block()` inserts a directory block record keyed by block number.
- `o2fsck_dir_block_iterate()` walks records in block order and optionally readaheads batches of up to 1024 directory blocks through vector I/O.
- Readahead is skipped if no I/O channel exists or cache size is too small.
- `o2fsck_search_reidx_dir()` and `o2fsck_try_add_reidx_dir()` manage a second rb-tree keyed by directory inode number.
- `o2fsck_rebuild_indexed_dirs()` truncates and rebuilds indexed directory trees for queued non-inline directories.

Dependencies: kernel-style rbtrees, libocfs2 malloc/free, `io_vec_read_blocks()`, `ocfs2_dx_dir_truncate()`, `ocfs2_dx_dir_build()`.

Risk notes:
- Insert logic assumes no duplicate directory block keys; equal keys leave the search loop without moving `p`, which would be unsafe if duplicates are inserted.
- Rebuild skips inline directories and expects index corruption decisions to be made by pass logic.
