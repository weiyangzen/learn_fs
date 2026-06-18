# File Research: sources/local-fs/ocfs2-tools/libocfs2/fileio.c

Purpose: file read/write helpers for libocfs2, including inline data, holes, unwritten extents, allocation on write, and inline-to-extent conversion.

Key responsibilities:
- Reads whole files through block iteration or inline-data copy.
- Reads aligned byte ranges from cached inodes.
- Writes aligned byte ranges to existing extents, holes, or unwritten extents.
- Allocates clusters for holes on write.
- Handles refcount COW before writes to refcounted files.
- Converts inline-data inodes to extent-backed inodes.
- Attempts inline writes when supported and space allows.

Important APIs:
- `ocfs2_read_whole_file()`
- `ocfs2_file_read()`
- `ocfs2_convert_inline_data_to_extents()`
- `ocfs2_file_write()`

Core read behavior:
- Inline data reads copy from `id2.i_data.id_data`.
- Direct file reads require count, offset, and buffer pointer alignment to block size.
- Holes and unwritten extents read as zeroes.
- Reads clamp to inode size.

Core write behavior:
- Block writes require block-aligned count, offset, and buffer.
- If writing a refcounted file on a refcount-tree filesystem, performs COW over affected clusters first.
- Holes allocate clusters, zero unwritten cluster edges, write requested blocks, insert extents, and persist the cached inode.
- Unwritten extents are written, then converted to written via `ocfs2_mark_extent_written()` and cached inode refresh.
- Inline writes either update inline data, convert to extents when too large, or enable inline data for empty suitable inodes.

Dependencies:
- Uses extent map lookup, cluster allocation/free, cached inode writes, refcount COW, directory block helpers, and extent flag-change helpers.

Notable behavior and risks:
- `ocfs2_file_write()` does not update `*wrote` on successful inline writes; callers must not assume block-write semantics there.
- `ocfs2_read_whole_file()` returns directly from the inline-data path after allocating `inode_buf`, bypassing the local cleanup.
- `insert` in `ocfs2_file_block_write()` is declared outside the write loop and reset only after successful insertion; current flow resets it after insertion, but changes here should keep loop-state isolation in mind.
- `empty_blocks()` writes one zero block at a time, favoring simplicity over batching.
