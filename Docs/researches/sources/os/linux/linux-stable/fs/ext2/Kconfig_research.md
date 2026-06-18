# File Research: sources/os/linux/linux-stable/fs/ext2/Kconfig

## Summary
Declares ext2 kernel configuration options and marks the ext2 driver deprecated.

## Main Contents
- `EXT2_FS`: tristate driver option, selecting `BUFFER_HEAD` and `FS_IOMAP`.
- `EXT2_FS_XATTR`: optional extended attribute support.
- `EXT2_FS_POSIX_ACL`: optional POSIX ACL support, dependent on xattrs and selecting `FS_POSIX_ACL`.
- `EXT2_FS_SECURITY`: optional security-label xattr handler support.

## Important Behavior
The help text warns that the ext2 driver does not properly support timestamps beyond `03:14:07 UTC on 19 January 2038`, advises using ext4 for ext2-format filesystems, and frames this code as a simple filesystem reference.

## Risks
Feature options are layered: POSIX ACL and security labels require xattr support. Disabling xattrs removes both ACL storage and security-label support from the ext2 build.
