# File Research: sources/os/linux/linux/fs/ecryptfs/super.c

Defines eCryptfs superblock operations and inode-cache behavior.

Key behavior:
- Allocates `struct ecryptfs_inode_info` from `ecryptfs_inode_info_cache`.
- Initializes each inode’s crypt-stat, lower-file mutex, lower-file refcount, and lower-file pointer.
- Frees inode private storage and destroys crypt-stat state during inode destruction.
- `statfs` delegates to the lower filesystem, then rewrites the filesystem magic and adjusts reported name length for encrypted filename constraints.
- `evict_inode` truncates page cache, clears the inode, and drops the lower inode reference.
- `show_options` emits active eCryptfs mount crypt options, including auth token signatures, cipher, key size, passthrough, xattr metadata, encrypted view, unlink sigs, and mount-auth-token-only mode.

Important interactions:
- `ecryptfs_sops` is the central superblock operation table used by mount setup.
- Mount option display depends on `ecryptfs_mount_crypt_stat`.
- Inode teardown asserts the lower file has already been released.
