# File Research: sources/os/linux/linux/fs/squashfs/xattr.c

Implements SquashFS xattr listing and get support.

`squashfs_listxattr()` walks an inode’s xattr entries from metadata, maps SquashFS xattr types to Linux handlers, enforces handler list visibility, copies visible names with namespace prefixes, and skips values.

`squashfs_xattr_get()` scans entries for a namespace/name match, handles out-of-line value references, validates buffer size, and reads the value.

Defines user, trusted, and security xattr handlers. Trusted listing requires `CAP_SYS_ADMIN`. Unknown xattr types are ignored.
