# File Research: sources/os/linux/linux-stable/fs/jffs2/security.c

This file integrates JFFS2 with Linux security xattrs and inode security labeling.

Key responsibilities:
- Implements `jffs2_initxattrs()` as the callback used by LSM inode initialization to attach initial security xattrs through `do_jffs2_setxattr()`.
- Exposes `jffs2_init_security()` as the filesystem hook that calls `security_inode_init_security()`.
- Provides `security.*` xattr get/set handlers backed by JFFS2 xattr prefix `JFFS2_XPREFIX_SECURITY`.
- Defines `jffs2_security_xattr_handler` with `XATTR_SECURITY_PREFIX`.

Important interactions:
- Used during inode creation after the initial raw inode node is written and before the parent dirent is committed.
- Depends on the generic LSM security-label API and JFFS2 xattr storage implementation.

Notable invariants and risks:
- Initial label attachment stops on the first failed xattr write.
- The set handler ignores idmap-specific behavior and delegates policy/storage to `do_jffs2_setxattr()`.
