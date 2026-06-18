# File Research: sources/os/linux/linux/fs/ext2/super.c

## Purpose
Implements ext2 filesystem registration, mount/remount, superblock validation, superblock lifecycle, statfs, sync/freeze handling, NFS export hooks, quota hooks, mount-option parsing, inode slab setup, and module init/exit.

## Main Responsibilities
- `ext2_fill_super()` is the central mount path: allocates `ext2_sb_info`, reads the on-disk superblock, validates magic/features/block size/inode size/group geometry/device size, loads group descriptors, initializes reservation windows, counters, xattr cache, quota ops, super ops, export ops, and root inode.
- `ext2_parse_param()` and `ext2_set_options()` implement the fs_context mount API and merge parsed options with on-disk defaults.
- `ext2_reconfigure()` handles remount transitions, including read-only/read-write state changes, quota suspend/resume, POSIX ACL flag updates, and refusal to change DAX while busy.
- `ext2_sync_super()`, `ext2_sync_fs()`, `ext2_write_super()`, `ext2_freeze()`, and `ext2_unfreeze()` maintain on-disk superblock counters and validity/error state.
- `ext2_error()` marks the filesystem errored, syncs the superblock, and applies `errors=continue|panic|remount-ro`.

## Integration Points
Registers `ext2_fs_type` through `register_filesystem()`, uses VFS `super_operations`, fs_context parsing, buffer-head block IO, quota APIs, DAX device discovery, xattr/ACL hooks, and generic NFS file-handle helpers.

## Important Behaviors
The mount path rejects unsupported incompatible features, rejects read-write mounts with unsupported read-only-compatible features, verifies group descriptors, validates root inode shape, and warns on unchecked/error/check-interval/max-mount-count states. DAX support is accepted only when the block device supports it and the block size equals page size; the driver logs a deprecation warning for ext2 DAX.

## Risks and Edge Cases
Most failure paths funnel through carefully ordered cleanup labels; future edits must preserve partial-initialization ordering. Remount state changes mix spinlock-protected superblock fields with quota and IO operations, so lock ordering matters. `statfs` caches overhead based on block count and updates free counters in the on-disk superblock image.
