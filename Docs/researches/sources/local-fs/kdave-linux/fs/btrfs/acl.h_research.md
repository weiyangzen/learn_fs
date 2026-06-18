# File Research: sources/local-fs/kdave-linux/fs/btrfs/acl.h

Purpose: Declares the Btrfs ACL API and provides stubs when POSIX ACL support is disabled.

Interfaces when `CONFIG_BTRFS_FS_POSIX_ACL` is enabled:
- `btrfs_get_acl(struct inode *, int type, bool rcu)`.
- `btrfs_set_acl(struct mnt_idmap *, struct dentry *, struct posix_acl *, int type)`.
- `__btrfs_set_acl(struct btrfs_trans_handle *, struct inode *, struct posix_acl *, int type)`.

Stub behavior when disabled:
- `btrfs_get_acl` and `btrfs_set_acl` are defined as `NULL`, matching VFS operation table expectations.
- `__btrfs_set_acl()` returns `-EOPNOTSUPP`.

Integration: Included by inode/xattr paths that need optional ACL support without scattering config checks across call sites.
