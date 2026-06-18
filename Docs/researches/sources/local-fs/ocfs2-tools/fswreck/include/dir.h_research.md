# File Research: sources/local-fs/ocfs2-tools/fswreck/include/dir.h

This header declares directory corruption helpers implemented in `dir.c`.

Exports:
- Directory inode, dot, dotdot, dirent, duplicate-parent, and disconnected-directory corruption functions.
- `create_directory()` helper.

Integration notes:
- `mess_up_dir_dot()` and `mess_up_dir_dotdot()` are declared but not implemented in the read `dir.c`; dot and dotdot corruptions are handled through `mess_up_dir_ent()` cases.
