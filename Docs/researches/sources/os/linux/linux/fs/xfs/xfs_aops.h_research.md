# File Research: sources/os/linux/linux/fs/xfs/xfs_aops.h

Header for XFS address-space operation exports and shared writeback helpers.

Key elements:
- Declares `xfs_address_space_operations`.
- Declares `xfs_dax_aops`.
- Declares `xfs_setfilesize`.
- Declares shared bio completion function `xfs_end_bio`.

Dependencies:
- Used by inode setup and I/O code that wires XFS into VFS address-space operations.

Research notes:
- The header exposes only the minimal cross-file surface from `xfs_aops.c`.
