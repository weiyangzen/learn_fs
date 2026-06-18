# File Research: sources/local-fs/ocfs2-tools/mkfs.ocfs2/mkfs.c

Main implementation of the OCFS2 filesystem formatter.

Key responsibilities:
- Parses command-line options for block size, cluster size, features, node slots, UUID, label, journal options, mount mode, cluster stack/name, heartbeat, discard, dry-run, force, and fs type.
- Computes default block/cluster/journal sizes and node slots.
- Opens the target device with direct I/O.
- Optionally discards device blocks.
- Clears both ends of the volume to remove stale metadata.
- Manually constructs initial OCFS2 superblock, root directory, system directory, system inodes, global bitmap, and allocator group.
- Writes all initial metadata with correct byte order and metadata ECC when enabled.
- Reopens the new filesystem with libocfs2 to finish higher-level structures: backup superblocks, journals, extent allocator growth, slot map, quotas, indexed directories, and `lost+found`.

Important top-level flow:
- `main()` sets signal handlers, initializes error tables, parses state, checks target safety, opens device, fills defaults, prints format plan, writes initial metadata, writes superblock, then calls `finish_normal_format()` unless formatting a heartbeat-only device.
- `finish_normal_format()` uses libocfs2 to finish filesystem initialization after the base image is readable.

Important functions:
- `get_state()`: option parsing and feature reconciliation.
- `fill_defaults()`: determines sizes, volume geometry, slot count, journal size, allocator reserve.
- `initialize_bitmap()` / `initialize_alloc_group()`: construct initial allocation metadata.
- `alloc_from_bitmap()` / `alloc_from_group()` / `alloc_inode()`: early allocator primitives.
- `add_entry_to_directory()`: builds root/system/orphan directory entries.
- `format_superblock()`: writes primary superblock dinode and feature fields.
- `format_file()`: writes system-file dinodes.
- `write_bitmap_data()`, `write_group_data()`, `write_directory_data()`.
- `format_journals()`, `format_slotmap()`, `format_backup_super()`.
- `index_system_dirs()`, `create_lost_found_dir()`.
- `mkfs_compute_meta_ecc()`: computes block checksums when metaecc is enabled.

Dependencies:
- libocfs2 feature parsing, metadata, directory, quota, journal, allocator, and slot-map APIs.
- libo2cb/libo2dlm safety checks via `check.c`.
- Linux direct I/O, `BLKDISCARD`, `/dev/urandom`.

Research notes:
- Initial filesystem creation is mostly manual because libocfs2 needs a readable filesystem before higher-level APIs can run.
- Feature flags are merged from feature level, explicit feature list, mount mode, cluster options, and heartbeat-device mode.
- Backup-super feature is cleared before primary superblock write, then set later by `format_backup_super()` after actual backup superblocks are written.
- `clear_both_ends()` is used both before formatting and as a failure cleanup path to reduce risk of leaving recognizable partial metadata.
