# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dblist_dir.c

Connects directory block lists to directory entry iteration. `ext2fs_dblist_dir_iterate` walks a dblist and invokes a directory-entry callback for each directory block.

Behavior:
- Builds a `struct dir_context` with flags, buffer, callback, private data, and error field.
- Uses caller-supplied block buffer or allocates one filesystem block.
- Calls `ext2fs_dblist_iterate2` with `db_dir_proc`.
- `db_dir_proc` reads the directory inode, chooses inline-data iteration for `EXT4_INLINE_DATA_FL`, otherwise calls `ext2fs_process_dir_block`.

Dependencies: dblist APIs, inode read, directory iteration internals, inline data directory iterator.

Implementation notes:
- `ctx->dir` is updated for each dblist entry.
- If `ext2fs_process_dir_block` returns `BLOCK_ABORT` without setting `ctx->errcode`, dblist iteration aborts.
- The function returns `ctx.errcode` after successful dblist traversal.
