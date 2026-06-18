# File Research: sources/os/linux/linux/fs/ufs/super.c

## Purpose
Implements UFS superblock, mount, remount, export, sync, statfs, inode-cache, and module registration logic for the Linux UFS filesystem driver.

## Main Contents
- NFS export support:
  - `ufs_nfs_get_inode()`, `ufs_fh_to_dentry()`, `ufs_fh_to_parent()`, `ufs_get_parent()`.
  - `ufs_export_ops` uses generic inode file handles with UFS inode lookup.
- Debug-only dump helpers for superblock and cylinder group state under `CONFIG_UFS_DEBUG`.
- Error reporting:
  - `ufs_error()` marks writable filesystems bad, schedules superblock dirtiness, and applies the configured `onerror` policy.
  - `ufs_panic()` marks bad and read-only while logging a panic-style message.
  - `ufs_warning()` logs nonfatal warnings.
- Mount option parsing:
  - `ufstype=` supports `old`, `sun`, `sunos`, `sunx86`, `44bsd`, `ufs2`/`5xbsd`, `hp`, `nextstep`, `nextstep-cd`, and `openstep`.
  - `onerror=` supports `panic`, `lock`, `umount`, and `repair`.
- Superblock loading:
  - `ufs_fill_super()` allocates `ufs_sb_info` and `ufs_sb_private_info`, selects geometry defaults by flavor, reads the on-disk superblock, probes byte order through magic values, validates fragment/block sizes, checks clean state, initializes derived geometry, loads root inode, and reads cylinder group structures for writable mounts.
- Cylinder summary handling:
  - `ufs_setup_cstotal()` normalizes variant-specific on-disk summary placement into in-memory `cs_total`.
  - `ufs_put_cstotal()` writes summary totals back to the correct UFS1/UFS2/44BSD locations.
  - `ufs_read_cylinder_structures()` reads cylinder summaries and cylinder group buffers, then prepares the small cylinder-group private-info cache.
  - `ufs_put_super_internal()` writes summaries and releases cylinder group resources.
- Sync and dirty scheduling:
  - `ufs_sync_fs()` updates timestamps/state and summary totals.
  - `ufs_mark_sb_dirty()` queues delayed sync work.
  - `delayed_sync_fs()` drains the delayed work item.
- Remount and visibility:
  - `ufs_reconfigure()` handles read-only/read-write transitions and updates `onerror`.
  - `ufs_show_options()` reports current `ufstype` and `onerror`.
  - `ufs_statfs()` reports block, inode, free-space, name-length, and fsid data.
- Inode cache and filesystem registration:
  - `ufs_alloc_inode()`, `ufs_free_in_core_inode()`, `init_inodecache()`, `destroy_inodecache()`.
  - `ufs_super_ops`, `ufs_context_ops`, `ufs_fs_type`, `init_ufs_fs()`, `exit_ufs_fs()`.

## Important Design Points
- The driver requires an explicit `ufstype` for safe operation, but defaults to `old` with a warning if omitted.
- Byte order is detected by trying little-endian first, then big-endian, using the superblock magic.
- Several flavors are forced read-only even if mounted read-write: old, NeXTstep, NeXTstep CD, OpenStep, and HP.
- Writable remounts are allowed only when write support is compiled and the flavor is one of Sun, SunOS, 44BSD, Sun x86, or UFS2.
- Clean-state checks can force a filesystem read-only if it is active, bad, unknown, or needs fsck.
- UFS2 expands timestamps and block pointers, so mount setup changes time granularity/ranges and `s_apbshift`.
- `ufs_max_bytes()` derives maximum file size from direct/single/double/triple indirect addressing and clamps to `MAX_LFS_FILESIZE`.

## Cross-File Relationships
- Uses on-disk structures and flags from `ufs_fs.h`.
- Uses endian helpers from `swab.h`.
- Uses buffer, bitmap, state, and superblock-offset helpers from `util.h`.
- Installs inode operations implemented in UFS inode/file/namei code via declarations in `ufs.h`.
- Calls cylinder APIs `ufs_put_cylinder()` and UFS inode APIs `ufs_iget()`, `ufs_write_inode()`, `ufs_evict_inode()`.

## Risks / Review Notes
- Wrong `ufstype` is explicitly warned as filesystem-corrupting; variant flags control directory encoding, UID encoding, state fields, cylinder-group format, and pointer width.
- `ufs_read_cylinder_structures()` returns boolean success rather than errno, so mount failures collapse to generic paths.
- Delayed sync scheduling depends on `dirty_writeback_interval`; superblock dirtiness is not written immediately in all paths.
- On write-capable mounts, summary and cylinder group writeback paths must preserve endian conversion and variant-specific placement.
