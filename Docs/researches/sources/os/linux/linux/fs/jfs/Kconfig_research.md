# File Research: sources/os/linux/linux/fs/jfs/Kconfig

## Purpose
Defines Linux Kconfig options for building IBM JFS support and optional JFS features.

## Options
- `JFS_FS`: tristate main filesystem option. Selects `BUFFER_HEAD`, `NLS`, `NLS_UCS2_UTILS`, `CRC32`, and `LEGACY_DIRECT_IO`.
- `JFS_POSIX_ACL`: optional ACL support, depends on `JFS_FS`, selects `FS_POSIX_ACL`.
- `JFS_SECURITY`: optional security-label xattr support for LSMs such as SELinux.
- `JFS_DEBUG`: optional additional debugging messages.
- `JFS_STATISTICS`: optional `/proc/fs/jfs/` statistics reporting.

## User-Facing Notes
- Main help points to `Documentation/admin-guide/jfs.rst`.
- ACL help suggests disabling ACLs when unfamiliar.
- Security label help recommends disabling unless an LSM requires xattr labels.
