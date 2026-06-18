# File Research: sources/teaching/minix/minix/fs/ext2/read.c

This file implements ext2 read/write transfer dispatch, block mapping reads, readahead, symlink block access, and `getdents`.

Key entry points:
- `fs_readwrite()`: shared read/write/peek handler that chunks I/O by filesystem block.
- `read_map()`: maps file offsets through direct, single, double, and triple indirect blocks.
- `get_block_map()`: maps and obtains a buffer for a file offset.
- `rd_indir()`: reads an indirect-block entry.
- `fs_getdents()`: emits directory entries through fsdriver dentry API.

Internal:
- `rw_chunk()` handles sparse reads as zeroes, peeks sparse blocks to VM as zero, allocates blocks on write, reads existing blocks, and copies to/from fsdriver data.
- `rahead()` performs cache lookup and prefetch planning, with minimum prefetch unless a seek occurred.
- `get_dtype()` maps ext2 directory file type fields to `DT_*` values.

Important behavior:
- Sparse file holes read as zero without block allocation.
- Writes beyond EOF allocate blocks through `new_block()`.
- Full-block writes may avoid reading old data.
- Directory iteration requires aligned positions and skips entries with `d_ino == 0`.

Notable issue:
- `fs_getdents()` has duplicate `assert(bp != NULL)`.
