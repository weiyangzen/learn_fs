# File Research: sources/local-fs/ocfs2-tools/libocfs2/closefs.c

Filesystem flush and close helpers.

`ocfs2_flush()` writes dirty global quota info for each quota type and writes the corresponding quota inode. `ocfs2_close()` flushes only when `OCFS2_FLAG_DIRTY` is set, then releases the filesystem object through `ocfs2_freefs()`.

This file has a narrow but important teardown role: quota write failures prevent close from freeing the filesystem, allowing callers to see and handle persistence errors.
