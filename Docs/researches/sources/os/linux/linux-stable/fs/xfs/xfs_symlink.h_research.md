# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_symlink.h

Small header declaring XFS kernel symlink operations.

Declarations:
- `xfs_symlink` creates a symlink inode and directory entry.
- `xfs_readlink` reads an inline or remote symlink target into a caller-provided buffer.
- `xfs_inactive_symlink` performs cleanup for symlinks during inode inactive processing.

Research notes:
- This header exposes only the high-level symlink operations; remote symlink block encoding and storage details are kept in the remote symlink helpers.
