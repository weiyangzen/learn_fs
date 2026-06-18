# File Research: sources/os/linux/linux-stable/fs/orangefs/Makefile

## Scope

This Makefile builds the OrangeFS kernel client module.

## Build Behavior

- Adds `orangefs.o` when `CONFIG_ORANGEFS_FS` is enabled.
- Links `orangefs.o` from ACL, file, cache, utils, xattr, dcache, inode, sysfs, module, superblock, request-device, namei, symlink, directory, buffer-map, debugfs, and waitqueue objects.

## Dependencies And Role

- Captures OrangeFS as one VFS module with both filesystem entry points and the `/dev/pvfs2-req` daemon bridge.
