# File Research: sources/os/linux/linux/fs/erofs/super.c

## Purpose
Implements the EROFS filesystem superblock, mount-context, option parsing, device setup, sysfs/export integration, inode-cache lifecycle, and module init/exit paths.

## Main Elements
- Logging and inode allocation: `_erofs_printk()`, `erofs_alloc_inode()`, `erofs_free_inode()`, and the `erofs_inode` slab cache.
- Metadata and superblock parsing: `erofs_read_metadata()`, `erofs_superblock_csum_verify()`, and `erofs_read_superblock()` validate magic, block size, incompatible features, checksum, 48-bit fields, metabox fields, xattr prefix locations, packed inode IDs, UUID, volume name, and compression configuration.
- Multi-device setup: `erofs_init_device()` and `erofs_scan_devices()` parse device slots, open block devices or backing files, register fscache cookies, probe DAX, track `total_blocks`, and manage an IDR-backed device context.
- Mount options: `erofs_fs_parameters[]`, `erofs_fc_parse_param()`, and `erofs_fc_set_dax_mode()` handle xattrs, ACLs, compressed-cache strategy, DAX, extra devices, fscache `fsid`, `domain_id`, direct I/O, filesystem offsets, and page-cache inode sharing.
- Export support: `erofs_encode_fh()`, `erofs_fh_to_dentry()`, `erofs_fh_to_parent()`, and `erofs_get_parent()` expose stable NID-based file handles.
- Mount construction: `erofs_fc_fill_super()` initializes `super_block` operations, file-backed/fscache/block-device mode, DAX constraints, compressed subsystem state, packed/metabox/root inodes, shrinker registration, xattr prefixes, sysfs name, and sysfs registration.
- Teardown and module lifecycle: `erofs_put_super()`, `erofs_kill_sb()`, `erofs_module_init()`, and `erofs_module_exit()` unwind sysfs, shrinker, internal inodes, fscache, DAX, device contexts, and compression subsystems.
- VFS callbacks: `erofs_statfs()`, `erofs_show_options()`, `erofs_evict_inode()`, and `erofs_sops`.

## Dependencies And Integration
This file is the top-level bridge between EROFS and VFS mount APIs, anonymous inode-backed modes, block-device/file-backed/fscache I/O, DAX, xattrs, POSIX ACLs, exportfs, sysfs, compression, shrinkers, and EROFS internal inode/name lookup code.

## Risk Notes
Mount correctness depends on strict validation of on-disk feature flags, block sizes, 48-bit fields, xattr prefix IDs, device counts, and metabox self-loop prevention. File-backed mounts explicitly reject stacked filesystems to avoid kernel stack recursion. Device and fscache setup have many partially initialized resources, so cleanup ordering is important. DAX and inode-share options are mutually constrained and may be silently disabled when unsupported.
