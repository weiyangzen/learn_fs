# File Research: sources/os/linux/linux/fs/efs/symlink.c

Implements EFS symlink page reading.

Key behavior:
- Rejects symlink targets longer than two EFS blocks.
- Reads up to the first 512 bytes from logical block 0.
- Reads a second block when needed.
- Copies the target into the folio, appends a NUL terminator, and completes folio read status.

Important interactions:
- Uses `efs_bmap()` to locate symlink data blocks.
- Installed as `efs_symlink_aops` by `efs_iget()`.
