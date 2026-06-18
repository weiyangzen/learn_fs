# File Research: sources/os/linux/linux-stable/fs/ecryptfs/super.c

## Summary
Defines eCryptfs superblock operations and inode allocation/destruction behavior.

## Main Responsibilities
- Allocates eCryptfs inode-private objects from `ecryptfs_inode_info_cache`.
- Initializes and destroys per-inode cryptographic state.
- Forwards `statfs()` to the lower filesystem while adjusting type/name length.
- Drops lower inode references on eviction.
- Emits mount options through `show_options()`.

## Key APIs
- `ecryptfs_sops`
- `ecryptfs_inode_info_cache`

## Important Behavior
Allocated inodes initialize `crypt_stat`, lower-file mutex/count state, and an empty lower-file pointer. Destruction asserts that the lower file has already been released, then destroys cryptographic state.

## Risks
Lifetime is stacked: eCryptfs inode teardown must release lower file and lower inode references exactly once. Mount option display walks global auth token state under its mutex.
