# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/smbfs_mount.h

This header defines the user/kernel mount argument interface for SMBFS.

Versioning:
- Major version is 1, minor is 3300, combined `SMBFS_VERSION` encodes both.
- Version string is `"1.33"`.
- VFS name is `"smbfs"`.

Mount options and flags:
- Defines ACL/noACL option strings.
- `SMBFS_MF_SOFT`, `SMBFS_MF_INTR`, and `SMBFS_MF_NOAC` control soft mounts, interruptibility, and attribute caching.
- Attribute cache flags mark which min/max file/dir cache times were explicitly set.

Mount argument structures:
- `smbfs_args` carries version, device fd, flags, uid/gid, file/dir modes, and attribute cache min/max values.
- Under `_SYSCALL32`, `smbfs_args32` provides fixed-width 32-bit syscall layout.

Dependencies and relationships:
- Used by `mount_smbfs` and the kernel SMBFS mount path.
- The file’s comments note origins from Darwin SMBFS definitions.
