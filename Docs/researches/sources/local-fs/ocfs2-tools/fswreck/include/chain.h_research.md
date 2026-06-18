# File Research: sources/local-fs/ocfs2-tools/fswreck/include/chain.h

This header declares chain and superblock cluster corruption entry points implemented in `chain.c`.

Exports:
- Chain list, record, inode, group, group magic, and CPG corruption functions.
- Superblock cluster excess/lack corruption functions.
- All functions accept `ocfs2_filesys *`, `enum fsck_type`, and slot number.

Integration notes:
- Included through `main.h`.
- Used by `corrupt.c` dispatch for system-file corruption codes.
