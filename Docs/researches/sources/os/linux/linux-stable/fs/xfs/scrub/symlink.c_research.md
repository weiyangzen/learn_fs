# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/symlink.c

Implements online scrub for symbolic links.

Key behavior:
- `xchk_setup_symlink` allocates a `XFS_SYMLINK_MAXLEN + 1` buffer before taking inode locks and, if repair is requested, asks symlink repair to reserve resources and create a tempfile.
- `xchk_symlink` validates that the target inode is a symlink, checks zapped health state, verifies plausible `i_disk_size`, and validates either local or remote symlink contents.
- Local symlinks are checked against available fork size and embedded string length.
- Remote symlinks are read via `xfs_symlink_remote_read`; the recovered buffer must contain a non-NUL target of at least the recorded length.
- A clean remote symlink clears the symlink-zapped health flag.

Important constraints:
- Non-symlink targets return `-ENOENT`.
- Invalid length or premature NUL terminators mark data fork block zero corrupt.
