# File Research: sources/os/linux/linux-stable/fs/squashfs/xattr.c

## Summary
Implements read-only VFS xattr listing and lookup for Squashfs user, trusted, and security namespaces.

## Key APIs
- `squashfs_listxattr()`.
- `squashfs_xattr_handlers`.

## Important Behavior
`squashfs_listxattr()` walks the inode's xattr entries, maps Squashfs xattr types to VFS handlers, applies handler list permissions, emits namespace prefixes plus names, and skips values.

`squashfs_xattr_get()` scans names for the requested namespace/name pair. If an entry has `SQUASHFS_XATTR_VALUE_OOL`, it follows an out-of-line xattr value reference before reading the value size and optional value bytes.

Trusted xattrs are listable only to `CAP_SYS_ADMIN`. Unknown xattr types are ignored.

## Risks
The code allocates a name-sized target buffer even for zero-length names and repeatedly advances metadata cursors through variable-length records. Size checks for caller buffers produce `-ERANGE`, while corrupt metadata read errors propagate from `squashfs_read_metadata()`.
