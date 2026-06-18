# File Research: sources/local-fs/xfsprogs/libxfs/iunlink.h

Header for userspace unlinked-inode list support.

Key responsibilities:
- Provides a stub `xfs_iunlink_lookup` returning NULL.
- Declares `xfs_iunlink_log_inode` and `xfs_iunlink_reload_next`.

Dependencies:
- Used by transaction/unlink handling code.

Notable risks:
- Consumers must not expect kernel-style lookup behavior from `xfs_iunlink_lookup`.
