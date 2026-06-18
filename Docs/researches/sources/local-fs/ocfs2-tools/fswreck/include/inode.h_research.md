# File Research: sources/local-fs/ocfs2-tools/fswreck/include/inode.h

This header declares inode, inline-data, and duplicate-cluster corruption helpers.

Exports:
- Field corruption, disconnected inode, orphaned inode, invalid inode allocation, inline flag, inline inode metadata, and duplicate cluster helpers.

Integration notes:
- Implemented in `inode.c`.
- Used mainly by `corrupt_file()` and `corrupt_sys_file()`.
