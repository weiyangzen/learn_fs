# File Research: sources/os/linux/linux/fs/jffs2/security.c

## Role

Integrates JFFS2 with Linux security xattrs and LSM inode security initialization.

## Key Responsibilities

- `jffs2_initxattrs()` attaches initial LSM-provided security xattrs using `do_jffs2_setxattr()`.
- `jffs2_init_security()` calls `security_inode_init_security()` for newly created inodes.
- Provides `security.*` xattr get/set handlers backed by JFFS2 prefix `JFFS2_XPREFIX_SECURITY`.
- Defines `jffs2_security_xattr_handler`.

## Important Interactions

- Used during inode creation after the initial raw inode has been written and before final directory entry commit.
- Delegates storage and policy enforcement to the generic LSM API and JFFS2 xattr implementation.

## Invariants and Risks

- Initial label setup stops on the first failed xattr write.
- The set handler ignores idmap-specific transformation and delegates directly to JFFS2 xattr storage.
