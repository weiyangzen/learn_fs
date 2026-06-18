# File Research: sources/local-fs/ocfs2-tools/libocfs2/expanddir.c

Purpose: expands and initializes OCFS2 directories.

Key responsibilities:
- Expands a directory by one cluster when all allocated blocks are used.
- Converts inline-data directories to extent-backed directories before expansion.
- Builds indexed directory structures after inline conversion or non-inline directory initialization when supported.
- Creates a fresh empty directory block with one free `ocfs2_dir_entry`.
- Initializes `.` and `..` entries.
- Updates the parent link count and child inode size.

Important APIs:
- `ocfs2_expand_dir()`
- `ocfs2_init_dir()`

Core invariants:
- Requires `OCFS2_FLAG_RW`.
- `ocfs2_expand_dir()` first validates the target is a directory.
- Directory `i_size` is assumed to be blocksize-aligned.
- When trailers are supported, new directory blocks reserve trailer space by setting the free dirent `rec_len` to `ocfs2_dir_trailer_blk_off()`.
- Inline directories use `id2.i_data.id_data` and `id_count`; non-inline directories use the first mapped block.

Dependencies:
- Uses `ocfs2_check_directory()`, cached inode read/write, `ocfs2_extend_allocation()`, `ocfs2_extent_map_get_blocks()`, directory block I/O, inline-data conversion, and `ocfs2_dx_dir_build()`.

Notable behavior and risks:
- In `ocfs2_init_dir()`, two corruption checks return directly after `buf` and `cinode` allocation, bypassing the cleanup path. Those should be treated as cleanup-risk paths if this code is modified.
- After `ocfs2_dx_dir_build()`, the code re-reads the cached inode because the builder can write changes outside the local cached copy.
