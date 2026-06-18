# File Research: sources/teaching/minix/minix/fs/isofs/link.c

This file implements readlink for isofs.

Entry point:
- `fs_rdlink(ino_nr, data, bytes)`: gets inode, verifies it is a symbolic link, copies up to requested bytes from Rock Ridge `s_name`.

Behavior:
- Returns `EINVAL` if inode is not cached/open.
- Returns `EACCES` if the inode mode is not symlink.
- Uses `fsdriver_copyout`.

Dependency:
- Symlink targets are populated by Rock Ridge `SL` records in `susp_rock_ridge.c`.
