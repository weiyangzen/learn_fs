# File Research: sources/os/linux/linux/fs/coda/inode.c

## Purpose
Implements Coda filesystem superblock, mount context, inode-cache, root setup, filesystem registration metadata, and common inode operations for getattr/setattr/statfs.

## Main Elements
- Inode cache lifecycle: `coda_init_inodecache()`, `coda_destroy_inodecache()`, `coda_alloc_inode()`, and `coda_free_inode()` manage `struct coda_inode_info` allocation and initialization.
- Mount parsing: supports modern `fd=` fs parameter and legacy binary `struct coda_mount_data`, mapping a Coda pseudo-device file descriptor to a `coda_comms[]` index.
- Superblock setup: `coda_fill_super()` validates the pseudo-device, binds `venus_comm` to the superblock, initializes superblock fields, asks Venus for the root fid, and builds the root inode/dentry.
- Superblock teardown: `coda_put_super()` clears `vc_sb` and `s_fs_info`; `coda_evict_inode()` truncates pages, clears inode state, and clears Coda cache state.
- VFS operations: `coda_getattr()`, `coda_setattr()`, and `coda_statfs()` route metadata operations to Venus and update VFS attributes on success.
- Filesystem type: `coda_fs_type` uses `get_tree_nodev`, `kill_anon_super`, `FS_BINARY_MOUNTDATA`, and rejects mounts outside the initial pid namespace.

## Dependencies And Integration
This file ties Coda VFS objects to the userspace Venus daemon through `venus_rootfid()`, `venus_setattr()`, and `venus_statfs()`. It depends on `coda_psdev.h` for device communications, `coda_linux.h` for inode/fid helpers, and `coda_cache.h` for cache invalidation. Module initialization and character-device setup live in `psdev.c`.

## Risk Notes
Mount correctness depends on exclusive pseudo-device binding under `vc_mutex`; stale `vc_sb` state would break communication with Venus. The legacy binary mount parser intentionally ignores some `fd` errors for compatibility. `coda_put_super()` destroys `vc_mutex`, so lifecycle ordering with pseudo-device release is sensitive.
