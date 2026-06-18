# File Research: sources/os/linux/linux/fs/squashfs/xattr.h

Declares xattr lookup helpers when `CONFIG_SQUASHFS_XATTR` is enabled.

When xattr support is disabled, provides stubs that still read enough of the on-disk xattr id table to find `xattr_table_start`, logs that xattrs will be ignored, and returns `-ENOTSUPP`.

Disabled builds define `squashfs_listxattr` and `squashfs_xattr_handlers` as `NULL`, while `squashfs_xattr_lookup()` becomes a no-op.
