# File Research: sources/local-fs/btrfs-linux/fs/btrfs/acl.h

Header for Btrfs POSIX ACL integration.

Key points:
- Declares `btrfs_get_acl()`, `btrfs_set_acl()`, and `__btrfs_set_acl()` when `CONFIG_BTRFS_FS_POSIX_ACL` is enabled.
- Provides disabled-config stubs:
  - `btrfs_get_acl` and `btrfs_set_acl` are `NULL`.
  - `__btrfs_set_acl()` returns `-EOPNOTSUPP`.
- Forward declares ACL, inode, dentry, idmap, and transaction types as needed.

Role in system:
- Lets the rest of Btrfs call ACL helpers without scattering config conditionals.
