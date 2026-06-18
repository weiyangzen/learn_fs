# File Research: sources/os/linux/linux-stable/fs/squashfs/xattr.h

## Summary
Declares xattr table and lookup helpers, with stub implementations when Squashfs xattr support is not compiled in.

## Main Contents
- Real extern declarations under `CONFIG_SQUASHFS_XATTR`.
- Stub `squashfs_read_xattr_id_table()` that reads the xattr table header enough to find the next table, logs that xattrs are ignored, and returns `-ENOTSUPP`.
- Stub `squashfs_xattr_lookup()` returning success without xattr data.
- Macro definitions that disable listxattr and xattr handlers.

## Risks
The no-xattr stub is still part of mount table ordering: it must return `xattr_table_start` so `super.c` can continue locating the id table even though xattrs are ignored.
