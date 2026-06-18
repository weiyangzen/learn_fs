# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/dirparents.c

Read coverage: complete file read, 153 lines.

Purpose: records directory parent relationships discovered during fsck so pass 3 can verify directory connectivity and `..` correctness.

Behavior:
- Stores `o2fsck_dir_parent` nodes in an rb-tree keyed by directory inode.
- Each record tracks the directory inode, its `..` target, the parent directory entry that points to it, connection status, loop number, and orphan-dir membership.
- Provides add, lookup, first, next, and remove helpers.

Dependencies: kernel-style rbtrees and pass-level directory metadata collection.

Risk notes:
- Add path assumes callers prevent duplicate directory inodes; duplicates return internal failure.
- Uses `calloc/free` directly rather than libocfs2 allocation wrappers.
