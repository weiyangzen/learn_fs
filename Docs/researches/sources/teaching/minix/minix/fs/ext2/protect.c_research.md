# File Research: sources/teaching/minix/minix/fs/ext2/protect.c

This file implements chmod and chown handlers.

Entry points:
- `fs_chmod(ino_nr, mode)`: updates permission bits while preserving file type and non-mode bits, marks ctime and inode dirty, returns full mode.
- `fs_chown(ino_nr, uid, gid, mode)`: changes owner/group, clears setuid/setgid bits, marks ctime and inode dirty, returns updated mode.

Dependencies:
- Uses `get_inode`, `put_inode`, and shared inode dirty/time flags.

Behavior:
- Permission and ownership policy checks are assumed to happen above the filesystem server; this layer applies requested metadata changes.
