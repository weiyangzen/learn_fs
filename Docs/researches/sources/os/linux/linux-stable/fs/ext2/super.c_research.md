# File Research: sources/os/linux/linux-stable/fs/ext2/super.c

## Purpose

`super.c` is the ext2 filesystem mount, superblock, lifecycle, quota, and module registration implementation. It wires ext2 into the Linux VFS through `file_system_type`, `super_operations`, `export_operations`, and `fs_context_operations`.

## Main Responsibilities

- Reports and handles filesystem errors via `ext2_error()`, including setting `EXT2_ERROR_FS`, syncing the superblock, panic-on-error, and remount-readonly behavior.
- Manages in-core ext2 superblock state in `struct ext2_sb_info`, including group descriptors, counters, reservation state, xattr block cache, DAX device reference, and quota hooks.
- Allocates and frees ext2 inode cache objects through `ext2_inode_cachep`, `ext2_alloc_inode()`, `ext2_free_in_core_inode()`, and `init_once()`.
- Parses mount parameters using the modern fs_context parser in `ext2_parse_param()`.
- Loads and validates the on-disk ext2 superblock and group descriptors in `ext2_fill_super()`.
- Provides remount/reconfigure logic in `ext2_reconfigure()`.
- Implements `statfs`, sync, freeze, unfreeze, NFS export inode lookup, and optional quota file I/O.
- Registers/unregisters the `ext2` filesystem module.

## Key Data and Operations

- `ext2_sops` provides VFS super operations: inode allocation/freeing, write/evict inode, put_super, sync, freeze/unfreeze, statfs, option display, and quota read/write when enabled.
- `ext2_export_ops` supports NFS export using 32-bit inode file handles and `ext2_get_parent`.
- `ext2_param_spec` accepts options such as `bsddf`, `minixdf`, `grpid`, `resuid`, `resgid`, `sb`, `errors=`, `nouid32`, `debug`, `oldalloc`, `orlov`, `user_xattr`, `acl`, `dax`, quotas, and `reservation`.
- `struct ext2_fs_context` records parsed mount options separately from persistent superblock state until mount/reconfigure applies them.
- `ext2_set_options()` combines parsed options with on-disk defaults, including default error behavior and reserved uid/gid.
- `ext2_fill_super()` performs the critical mount path: allocate `sbi`, set block size, read superblock, validate feature flags, validate block/inode geometry, read group descriptors, initialize counters, create xattr cache, set VFS operations, load root inode, and mark the filesystem mounted.
- `ext2_check_descriptors()` verifies each group’s block bitmap, inode bitmap, and inode table lie inside the group.
- `ext2_max_size()` computes ext2 maximum file size from block size and indirect block limits.
- `descriptor_loc()` handles descriptor block placement, including meta block groups.
- `ext2_sync_super()`, `ext2_sync_fs()`, `ext2_freeze()`, and `ext2_unfreeze()` update free counts, timestamps, and valid/error state.
- Quota support directly reads/writes quota files through `ext2_get_block()` and buffer heads, bypassing page cache assumptions.

## Notable Behavior

- DAX mount support is present but emits a deprecation warning saying ext2 DAX support will be removed at the end of 2025 and recommends ext4.
- Unsupported incompatible features abort mount; unsupported readonly-compatible features abort read-write mount.
- Ext3-with-journal filesystems can be mounted as ext2 with a warning.
- Remount refuses to change the DAX flag while busy inodes may exist.
- Read-only remount restores valid filesystem state only when appropriate; read-write remount rechecks readonly-compatible feature support.
- On writeable mounts, `ext2_setup_super()` increments mount count and warns about unchecked, errored, over-mounted, or stale-checktime filesystems.

## Dependencies

- Uses `ext2.h`, `xattr.h`, and `acl.h` for ext2 layout, xattr, and ACL integration.
- Relies on Linux VFS, buffer heads, fs_context, quota, DAX, exportfs, percpu counters, and block device helpers.
- Calls into other ext2 units such as inode loading/writing, block counting, reservation windows, group descriptor helpers, and xattr cache creation/destruction.

## Research Notes

This file is the best entry point for understanding ext2 mount-time trust boundaries. The mount path is heavily validation-oriented: feature bits, block size, inode size, group descriptor placement, group/inode counts, root inode shape, and backing-device size are all checked before the filesystem becomes live.
