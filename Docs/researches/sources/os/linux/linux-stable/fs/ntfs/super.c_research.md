# File Research: sources/os/linux/linux-stable/fs/ntfs/super.c

This is the legacy `fs/ntfs` driver superblock, mount, system-file bootstrap, free-space accounting, and module lifecycle implementation. It owns `struct file_system_type ntfs_fs_type`, the `super_operations`, fs-context option parsing, the mount-time load of core NTFS metadata files, and unmount/sync/shutdown behavior.

Main responsibilities:
- Defines mount parameters for ownership, masks, NLS/charset, error policy, system/hidden file visibility, case sensitivity, sparse/discard behavior, ACLs, MFT zone multiplier, preallocation size, and Windows-name checking.
- Implements `ntfs_reconfigure()` with conservative read-write remount checks: existing volume errors, dirty/unsupported flags, chkdsk modification flags, logfile clearing, and quota-out-of-date marking can force failure or read-only behavior.
- Validates and parses the NTFS boot sector, deriving sector size, cluster size, MFT/index record sizes, volume cluster count, `$MFT` and `$MFTMirr` LCNs, mirror size, serial number, and sparse compression unit.
- Loads critical NTFS metadata in mount order: `$MFT`, `$MFTMirr`, `$MFT/$BITMAP`, `$UpCase`, `$AttrDef`, `$Bitmap`, `$Volume`, `$LogFile`, root, `$Secure`, `$Extend`, and optional `$Quota/$Q`.
- Compares `$MFT` and `$MFTMirr`, checks logfile state, detects Windows hibernation through `hiberfil.sys`, and handles dirty/unsupported volume flags.
- Maintains volume flags and label writes through resident `$Volume` attributes.
- Tracks free clusters and free MFT records by scanning `$Bitmap` and `$MFT/$BITMAP`; cluster scanning is queued on `ntfs-bg-io` after mount.
- Implements unmount cleanup, dirty-bit clearing on clean writable unmount, inode commits, block flushes, shutdown via `FS_IOC_SHUTDOWN`, `statfs`, module cache creation/destruction, sysctl registration, and filesystem registration.

Important functions and data:
- `ntfs_parse_param()` maps fs_context parameters to `struct ntfs_volume` fields and `NVol*` flags.
- `ntfs_handle_error()` applies `errors=panic|remount-ro|continue`, including writeback shutdown tracking for `-ENODEV`.
- `ntfs_write_volume_flags()`, `ntfs_set_volume_flags()`, `ntfs_clear_volume_flags()`, and `ntfs_write_volume_label()` update `$Volume` metadata.
- `is_boot_sector_ntfs()`, `read_ntfs_boot_sector()`, and `parse_ntfs_boot_sector()` form the boot-sector validation path.
- `ntfs_setup_allocators()` initializes MFT/data allocation zones based on `mft_zone_multiplier`.
- `load_system_files()` is the main metadata bootstrap routine and centralizes fallback-to-read-only decisions for damaged or unsafe volumes.
- `get_nr_free_clusters()`, `ntfs_available_clusters_count()`, and `__get_nr_free_mft_records()` populate allocation statistics used by `statfs` and allocation decisions.
- `ntfs_fill_super()` is the mount entry point used by `get_tree_bdev()`.
- Global caches: `ntfs_name_cache`, `ntfs_inode_cache`, `ntfs_big_inode_cache`, `ntfs_attr_ctx_cache`, and `ntfs_index_ctx_cache`.

Notable implementation details:
- Uses a global default `$UpCase` table with `ntfs_nr_upcase_users` under `ntfs_lock`; volumes use their own `$UpCase` unless it matches the generated default.
- Temporarily disables lockdep during NTFS mount bootstrap because metadata inode loading has exceptional locking order.
- Uses separate lock classes for system-file inodes such as `$MFTMirr`, `$Bitmap`, and `$MFT/$BITMAP`.
- `lcn_empty_bits_per_page` caches empty-bit counts for `$Bitmap` pages, complementing the atomic `free_clusters` and `dirty_clusters` counters.
- The mount path sets `s_time_gran = 100`, matching NTFS 100 ns timestamps, and enables idmapped mounts with `FS_ALLOW_IDMAP`.

Research notes:
- The file has been updated for read-write support and modern fs_context APIs, while still retaining legacy NTFS driver naming and metadata assumptions.
- Safety policy is strongly Windows-aware: dirty, chkdsk-modified, hibernated, unsupported-flag, or logfile-error states usually prevent writable operation.
- This file is the primary integration point between NTFS on-disk metadata validation and Linux VFS lifecycle semantics.
