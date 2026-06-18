# File Research: sources/os/linux/linux/fs/orangefs/super.c

## Role

Implements OrangeFS superblock lifecycle, mount context parsing, inode cache management, statfs, remount support, export file handles, and teardown.

## Main Responsibilities

- Defines global `orangefs_superblocks` list and lock for active OrangeFS mounts.
- Parses mount flags `acl`, `intr`, and `local_lock` via `fs_context`.
- Allocates private OrangeFS inodes from `orangefs_inode_cache`, initializing ref handles, fs IDs, failed-block state, and symlink target storage.
- Frees per-inode cached xattrs before returning inodes to the slab cache.
- `orangefs_statfs()` issues `ORANGEFS_VFS_OP_STATFS` and fills `kstatfs`.
- `orangefs_remount()` re-sends mount information to userspace client-core with priority/no-mutex semantics, then queries feature bits for userspace version `>= 20906`.
- Export support encodes OrangeFS handles and fs IDs into file handles.
- `orangefs_get_tree()` performs the userspace mount upcall, allocates an anonymous superblock, fills root inode/dentry, registers the superblock in the global list, and queries features.
- `orangefs_kill_sb()` sends the unmount upcall, removes the superblock from the list, synchronizes with remount-all, and frees private superblock data.

## Important Control Flow

Mount setup starts with `orangefs_init_fs_context()`, which allocates `orangefs_sb_info_s` and installs `orangefs_context_ops`. `orangefs_get_tree()` requires `fc->source`, sends `ORANGEFS_VFS_OP_FS_MOUNT`, validates non-null `fs_id`, creates an anonymous superblock, calls `orangefs_fill_sb()`, and only then links the mount into `orangefs_superblocks`.

Failure paths are careful: if `sget_fc()` succeeds but fill fails, `deactivate_locked_super()` lets `orangefs_kill_sb()` perform the unmount request, with `no_list` set because the superblock was never added to the global list.

## Data and ABI Notes

`orangefs_inode_cache_initialize()` uses `kmem_cache_create_usercopy()` and marks only the `link_target` field as usercopy-safe.

## Dependencies

Uses OrangeFS operation service helpers, root inode lookup (`orangefs_iget()`), xattr handlers, dentry ops, export ops, and the shared request mutex.

## Research Notes

This file is the mount/session authority for OrangeFS. It coordinates kernel superblocks with the userspace client’s dynamic mount table and is sensitive to restart/remount ordering.
