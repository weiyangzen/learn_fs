# File Research: sources/os/linux/linux/fs/9p/Makefile

## Summary
Builds the 9p filesystem module/object composition.

## Main Contents
- Builds `9p.o` when `CONFIG_9P_FS` is enabled.
- Core objects include superblock, inode, dotl inode, address-space, file, directory, dentry, session, fid, and xattr code.
- Adds `cache.o` when `CONFIG_9P_FSCACHE` is enabled.
- Adds `acl.o` when `CONFIG_9P_FS_POSIX_ACL` is enabled.

## Risks
Optional ACL and cache source files are linked only when their configuration symbols are enabled, so callers rely on header stubs for disabled ACL builds.
