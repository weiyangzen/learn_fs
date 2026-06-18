# File Research: sources/os/linux/linux/fs/ext2/xattr.h

## Purpose
Defines ext2 on-disk extended attribute format, alignment helpers, namespace indexes, and xattr API declarations or stubs.

## Main Responsibilities
- Declares `ext2_xattr_header` and `ext2_xattr_entry`.
- Defines namespace indexes for user, POSIX ACL access/default, trusted, Lustre, and security attributes.
- Provides alignment/size macros: `EXT2_XATTR_LEN`, `EXT2_XATTR_NEXT`, and `EXT2_XATTR_SIZE`.
- Exposes get/set/list/delete/cache APIs when `CONFIG_EXT2_FS_XATTR` is enabled.
- Provides `-EOPNOTSUPP` stubs and null handlers when xattr support is disabled.
- Declares or stubs `ext2_init_security()` based on `CONFIG_EXT2_FS_SECURITY`.

## Integration Points
Included by ext2 inode, symlink, ACL, security, and xattr implementation files. It bridges VFS xattr handlers with ext2’s disk layout.

## Risks and Edge Cases
The layout macros define the parser/writer contract for `xattr.c`; changing padding or entry sizing would alter disk compatibility.
