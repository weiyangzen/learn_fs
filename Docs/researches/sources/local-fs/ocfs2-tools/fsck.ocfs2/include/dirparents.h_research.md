# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/dirparents.h

Read coverage: complete file read, 59 lines.

Purpose: declares directory-parent records used to validate parentage and connectivity.

Key data:
- `dp_ino`: directory inode.
- `dp_dot_dot`: inode referenced by `..`.
- `dp_dirent`: inode containing the directory entry that points to this directory.
- `dp_connected`, `dp_loop_no`, and `dp_in_orphan_dir` are pass 3 connectivity state.

Key API: add, lookup, first, next, and remove helpers.

Dependencies: kernel rbtree API.
