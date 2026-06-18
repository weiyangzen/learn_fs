# File Research: sources/os/linux/linux/fs/ntfs/super.c

Read coverage: complete file, 2786 lines.

This is the legacy `ntfs` filesystem driver's superblock and module lifecycle implementation. It owns mount option parsing, filesystem context allocation, boot sector validation, metadata bootstrap, VFS super operations, free-space accounting, dirty-volume handling, shutdown, and module cache/workqueue setup.

Key entry points and exports:
- `ntfs_parse_param()` parses fs_context options such as `uid`, `gid`, masks, NLS/charset, `errors=`, `show_sys_files`, case-sensitivity toggles, sparse/preallocation behavior, hidden-file behavior, Windows-name checking, ACLs, discard, and remount-sensitive `mft_zone_multiplier`.
- `ntfs_reconfigure()` handles remount transitions, especially read-only to read-write safety checks against volume errors, dirty flags, chkdsk-modified flags, unsupported volume flags, logfile emptying, and quota state.
- `ntfs_handle_error()`, `ntfs_set_volume_flags()`, `ntfs_clear_volume_flags()`, and `ntfs_write_volume_label()` provide shared volume-state mutation helpers.
- `ntfs_fill_super()` is the core mount path. It reads and validates the NTFS boot sector, derives sector/cluster/MFT/index sizes, initializes allocator zones, loads `$MFT`, creates or references the global upcase table, loads system metadata files, creates the root dentry, computes free MFT records, and queues background free-cluster precomputation.
- `ntfs_put_super()`, `ntfs_sync_fs()`, `ntfs_force_shutdown()`, and `ntfs_statfs()` implement VFS superblock behavior.
- `init_ntfs_fs()` / `exit_ntfs_fs()` create and destroy slab caches, the workqueue, optional debug sysctls, and register/unregister filesystem type `"ntfs"`.

Core control flow:
- Boot validation starts in `is_boot_sector_ntfs()` and `read_ntfs_boot_sector()`, then `parse_ntfs_boot_sector()` enforces supported sector, cluster, MFT-record, index-record, cluster-count, and mirror-LCN constraints.
- `load_system_files()` is the metadata bootstrap hub. It loads/checks `$MFTMirr`, `$MFT/$BITMAP`, `$UpCase`, `$AttrDef`, `$Bitmap`, `$Volume`, `$LogFile`, root directory, hibernation status, and NTFS 3.x metadata such as `$Secure`, `$Extend`, and `$Quota`.
- The driver is conservative around write mounts: dirty/unsupported flags, hibernation, logfile failures, mirror mismatch, and quota problems can force read-only mode and set `NVolErrors()`.
- Free-space accounting is split between MFT record bitmap scanning and cluster bitmap scanning. Cluster scanning is done lazily in `precalc_free_clusters()` on `ntfs_wq`; waiters use `NVolFreeClusterKnown`.

Integration points:
- Uses kernel fs_context API, `get_tree_bdev()`, block device helpers, folios/page cache, slab caches, lockdep classes, NLS tables, xattr handlers, export ops, inode operations from sibling NTFS files, and the `volume.h` `ntfs_volume` state structure.
- Interacts with NTFS system files through inode and attribute helpers such as `ntfs_iget()`, `ntfs_attr_iget()`, `ntfs_attr_lookup()`, `ntfs_empty_logfile()`, `ntfs_mark_quotas_out_of_date()`, `ntfs_read_inode_mount()`, and MFT record mapping helpers.

Risks and invariants:
- Mount bootstrap uses many goto cleanup paths; ownership of system inodes, upcase references, NLS tables, and `lcn_empty_bits_per_page` is the main correctness risk.
- Write enablement depends on volume flags, hibernation detection, and logfile state; mistakes here risk Windows/NTFS consistency.
- `check_mft_mirror()` compares mirror records and runlists and must keep folio mappings balanced on all error paths.
- Free-cluster users can wait on `free_waitq`; initialization order and `NVolFreeClusterKnown` transitions are important for avoiding hangs.
