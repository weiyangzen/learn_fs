# File Research: sources/os/linux/linux/fs/ramfs/internal.h

Small internal ramfs header.

Defines:
- External declaration for `ramfs_file_inode_operations`.

Research notes:
- Included by ramfs implementation files so common inode code can refer to the file inode operations supplied by the selected MMU/NOMMU file implementation.
