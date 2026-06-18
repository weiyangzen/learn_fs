# File Research: sources/os/linux/linux-stable/fs/jfs/Kconfig

Defines build-time JFS configuration.

Options:
- `JFS_FS`: tristate filesystem support, selecting buffer heads, NLS, UCS-2 helpers, CRC32, and legacy direct I/O.
- `JFS_POSIX_ACL`: optional POSIX ACL support, selecting `FS_POSIX_ACL`.
- `JFS_SECURITY`: optional security-label xattr support for LSMs such as SELinux.
- `JFS_DEBUG`: optional debug logging.
- `JFS_STATISTICS`: optional `/proc/fs/jfs/` statistics.

Integration:
- These symbols control conditional compilation in ACL, debug/proc, xattr/security, and Makefile object inclusion.
