# File Research: sources/os/linux/linux/fs/nilfs2/export.h

This header declares NILFS2 export support structures for NFS/exportfs integration.

Key contents:
- Declares external `nilfs_export_ops`.
- Defines packed `struct nilfs_fid`, containing:
  - checkpoint number
  - inode number
  - inode generation
  - parent generation
  - parent inode number

Important role:
- NILFS2 is checkpoint-oriented, so exported file handles need checkpoint context in addition to inode identity.
- Parent fields support reconnecting directory hierarchy information for export operations.
