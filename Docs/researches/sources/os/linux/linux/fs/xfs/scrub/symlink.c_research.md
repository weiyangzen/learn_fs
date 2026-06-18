# File Research: sources/os/linux/linux/fs/xfs/scrub/symlink.c

This file implements online scrub for symbolic links. It validates symlink type, target length, local fork contents, remote symlink block readability, and target null-termination behavior.

Entry points:
- `xchk_setup_symlink(struct xfs_scrub *sc)`: allocates a max-length target buffer, optionally sets up repair resources, then delegates inode-content setup.
- `xchk_symlink(struct xfs_scrub *sc)`: validates the symlink target.

Scrub behavior:
1. Rejects non-symlink inodes with `-ENOENT`.
2. If the symlink looks zapped via `XFS_SICK_INO_SYMLINK_ZAPPED`, marks data fork corrupt.
3. Checks `i_disk_size` is `1..XFS_SYMLINK_MAXLEN`.
4. For local-format symlinks, checks the size fits in the inode data fork and that a string-length scan reaches at least `i_disk_size`.
5. For remote symlinks, reads target bytes with `xfs_symlink_remote_read`, processes read errors through scrub error handling, then verifies the target buffer contains enough non-NUL bytes.
6. Marks the symlink zapped flag healthy if a remote symlink reads cleanly.

Dependencies:
- `xfs_symlink.h` and `xfs_symlink_remote.h` provide symlink format and remote read helpers.
- `scrub/common.h` supplies setup, corrupt marking, and error-processing helpers.
- `scrub/repair.h` supplies `xrep_setup_symlink` when repair is possible.

Risk notes:
- On-disk symlink targets are not NUL-terminated, so this scrubber uses bounded `strnlen` checks against expected length.
- The setup buffer is `XFS_SYMLINK_MAXLEN + 1` so repair/scrub code can NUL-terminate safely.
