# File Research: sources/os/linux/linux-stable/fs/hfsplus/xattr_security.c

## Purpose

Provides the `security.*` xattr namespace handler and initial security-label setup for HFS+ inodes.

## Main Entry Points

- `hfsplus_security_getxattr()` and `hfsplus_security_setxattr()`: delegate to the core HFS+ xattr helpers with `XATTR_SECURITY_PREFIX`.
- `hfsplus_init_security()`: calls `security_inode_init_security()` with an HFS+ callback.
- `hfsplus_initxattrs()`: writes security xattrs supplied by the LSM during inode creation.
- `hfsplus_xattr_security_handler`: VFS handler descriptor.

## Control Flow And State

Initialization allocates a maximum-sized HFS+ xattr name buffer, skips empty security names, prefixes each LSM name with `security.`, and writes it through `__hfsplus_setxattr()`.

## Dependencies

Depends on Linux security hooks, xattr namespace constants, HFS+ xattr core helpers, and HFS+ attribute name length limits.

## Risks

Security-label persistence depends on HFS+ attributes-tree creation during inode initialization. Any failure stops the loop and returns the first error, potentially aborting inode creation or leaving only earlier labels written.
