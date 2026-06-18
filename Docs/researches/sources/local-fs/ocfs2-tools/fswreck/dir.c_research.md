# File Research: sources/local-fs/ocfs2-tools/fswreck/dir.c

This file creates directory and dirent corruptions for fsck testing.

Key behavior:
- `create_directory()` creates a uniquely named directory under a parent using `ocfs2_new_inode()`, `ocfs2_init_dir()`, and `ocfs2_link()`.
- Dirent iterator helpers rename entries, alter inode numbers, and alter record lengths via `ocfs2_dir_iterate()`.
- `damage_dir_content()` injects dirent-level corruptions:
  - duplicate `.`
  - rename `.` away from dot
  - invalid `.` or `..` inode number
  - excessive dot record length
  - zero-length/zero-name entry
  - invalid slash-containing name
  - out-of-range inode
  - free inode reference
  - mismatched file type
  - duplicate names
  - invalid record length
- `mess_up_dir_ent()` creates a child directory and corrupts its content.
- `mess_up_dir_parent_dup()` creates one directory linked from two parents.
- `mess_up_dir_inode()` corrupts directory inode extent state, including an empty directory extent list (`DIR_ZERO`) or manipulated extent records creating a directory hole (`DIR_HOLE`).
- `mess_up_dir_not_connected()` creates an initialized directory inode without linking it into any parent.

Integration notes:
- Relies on helpers from `extent.c` and `corrupt.c` for creating files/directories.
- Uses `mktemp()`, intentionally noted by comments as acceptable for this Linux-only utility.
- Several corruption paths assume non-inline directory data or enough generated entries to create extents.
