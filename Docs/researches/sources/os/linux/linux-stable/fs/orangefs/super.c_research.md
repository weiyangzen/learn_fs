# File Research: sources/os/linux/linux-stable/fs/orangefs/super.c

## Scope

This file implements OrangeFS superblock lifecycle, mount context parsing, inode slab allocation/freeing, statfs, remount after userspace client restart, export file handles, mount/unmount upcalls, root inode setup, superblock list management, and inode-cache initialization/finalization.

## Public And Internal APIs Covered

- Mount parameters: `orangefs_fs_param_spec`, `orangefs_parse_param()`, `orangefs_show_options()`, `orangefs_init_fs_context()`.
- Inode cache: `orangefs_inode_cache_initialize()`, `orangefs_inode_cache_finalize()`, allocator/free/destructor callbacks.
- Super operations: `orangefs_s_ops` with alloc/free/destroy/write_inode/drop_inode/statfs/show_options.
- Filesystem operations: `orangefs_statfs()`, `orangefs_reconfigure()`, `orangefs_remount()`, `orangefs_kill_sb()`.
- Export operations: `orangefs_encode_fh()` and `orangefs_fh_to_dentry()`.
- Mount helpers: `orangefs_get_tree()`, `orangefs_fill_sb()`, `orangefs_unmount()`.
- Stub fsid key table functions: `fsid_key_table_initialize()` and `fsid_key_table_finalize()`.

## Control Flow And Behavior

- Mount context allocation creates `struct orangefs_sb_info_s`, clears default option bits, and installs fs context operations.
- Mount options support `acl`, `intr`, and `local_lock`; reconfigure updates only runtime OrangeFS option bits, while `acl` updates superblock flags through fs context parsing.
- `orangefs_get_tree()` sends `ORANGEFS_VFS_OP_FS_MOUNT` to userspace with the source server string, validates a non-null fs id, creates an anonymous superblock, fills it, stores the source devname, adds the private superblock to the global list, and negotiates features for userspace version 2.9.6 or newer.
- `orangefs_fill_sb()` installs xattr handlers, magic, super ops, dentry ops, block size, max file size, bdi, root inode/dentry, and export ops.
- `orangefs_remount()` is used after client-core restart. It sends a priority mount operation while the request mutex is already held, updates the transient mount id, clears `mount_pending`, and refreshes feature flags.
- `orangefs_kill_sb()` kills the anonymous superblock, sends a userspace unmount operation, removes the OrangeFS private superblock from the global list, waits for any remount-all loop to finish with the request mutex, and frees private superblock memory.
- File handle encoding stores a 16-byte OrangeFS handle plus fs id, optionally followed by parent handle and fs id.

## State And Data Structures

- Global state: `orangefs_inode_cache`, `orangefs_superblocks`, `orangefs_superblocks_lock`, and `orangefs_features`.
- Private superblock state includes root handle, fs id, transient id, device name, option flags, list linkage, `mount_pending`, `no_list`, and back-pointer to `struct super_block`.
- Private inode objects are slab allocated and preserve initialized `vfs_inode` and `xattr_sem` while resetting handle, fs id, failed block index, and symlink target storage.

## Dependencies

- Uses OrangeFS operation service path for mount, unmount, statfs, feature negotiation, and write_inode setattr.
- Uses VFS fs_context, anonymous superblocks, exportfs, dentry root creation, bdi setup, inode slab APIs, seq_file option reporting, and POSIX ACL superblock flag handling.
- Depends on OrangeFS inode lookup `orangefs_iget()`, dentry ops, xattr handlers, and request mutex/list coordination from other OrangeFS files.

## Risks And Invariants

- Mount failure after a userspace mount response must send an unmount or deactivate the locked superblock to avoid stale client-core mount state.
- `no_list` tracks partially initialized superblocks so kill paths do not remove unlisted entries.
- The private inode cache is created with a usercopy region limited to `link_target`.
- Superblock list manipulation is protected by `orangefs_superblocks_lock`, while teardown also synchronizes with request-mutex users that may traverse mounts for remount-all.
