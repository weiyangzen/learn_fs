# File Research: sources/os/linux/linux/fs/ext2/Kconfig

Read status: complete, 50 lines.

This Kconfig file defines ext2 build-time configuration options.

Key responsibilities:
- Defines `EXT2_FS` as a tristate option for “Second extended fs support (DEPRECATED)”.
- Selects `BUFFER_HEAD` and `FS_IOMAP` for the ext2 driver.
- Documents ext2 deprecation due to insufficient timestamp support beyond 03:14:07 UTC on 19 January 2038.
- Advises users to mount ext2 filesystems with the ext4 driver instead.
- Defines optional support for extended attributes, POSIX ACLs, and security labels.

Options:
- `EXT2_FS_XATTR`: enables extended attributes.
- `EXT2_FS_POSIX_ACL`: depends on xattrs and selects `FS_POSIX_ACL`.
- `EXT2_FS_SECURITY`: depends on xattrs and enables security-label xattr handlers such as SELinux labels.

Research notes:
- The file explicitly frames ext2 as retained mainly as a simple reference filesystem for developers.
- Optional ACL/security features are layered on xattr support.
