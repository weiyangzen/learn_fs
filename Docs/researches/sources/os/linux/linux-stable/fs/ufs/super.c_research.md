# File Research: sources/os/linux/linux-stable/fs/ufs/super.c

## Summary
Implements UFS superblock handling: mount option parsing, filesystem flavor setup, superblock probing and validation, cylinder-group summary loading, sync/remount/statfs, export operations, inode cache setup, and module registration.

## Key APIs
- Mount/export: `ufs_fill_super()`, `ufs_get_tree()`, `ufs_reconfigure()`, `ufs_show_options()`, `ufs_statfs()`.
- Diagnostics/error policy: `ufs_error()`, `ufs_panic()`, `ufs_warning()`.
- Sync/lifetime: `ufs_sync_fs()`, `ufs_mark_sb_dirty()`, `ufs_put_super()`.
- NFS export helpers: `ufs_nfs_get_inode()`, `ufs_fh_to_dentry()`, `ufs_fh_to_parent()`, `ufs_get_parent()`.
- Module setup: `init_ufs_fs()`, `exit_ufs_fs()`.

## Important Behavior
Mount parameters support `ufstype=` and `onerror=` through the fs-context parser. `ufstype` is fixed at mount and cannot be changed during remount; `onerror` may be updated.

`ufs_fill_super()` initializes `ufs_sb_info`, chooses flavor-specific defaults for old UFS, Sun, SunOS, Sun x86, 44BSD, UFS2, HP, NeXTstep, NeXTstep CD, and OpenStep, then reads the on-disk superblock. Unsupported write modes are forced read-only for older/flavor-limited variants.

The superblock probe detects little-endian or big-endian media by trying known UFS magic values. NeXT/OpenStep probing can retry shifted `s_sbbase` locations. Fragment and block sizes must be powers of two and within accepted ranges before blocksize is finalized.

Clean-state handling marks unclean, active, bad, or fsck-needed filesystems read-only. For Sun-style state encodings, clean state is checked through `ufs_get_fs_state()` against `UFS_FSOK - fs_time`.

After validation, the file copies on-disk geometry into `ufs_sb_private_info`, computes derived masks/shifts, inode/addressing parameters, free-space reserve thresholds, max fast symlink length, max file size, root inode, and cylinder-group summaries for read-write mounts.

`ufs_read_cylinder_structures()` loads cylinder summary blocks and validates all cylinder-group headers. `ufs_put_super_internal()` writes summary state and releases loaded cylinder-group resources.

Sync updates `fs_time`, Sun-style fs state, and cylinder summary totals. Dirty superblocks are synced lazily through delayed work. Remount read-only writes summaries and clean state; remount read-write reloads cylinder structures and is allowed only for supported writable flavors.

## Dependencies
Uses buffer-head I/O, UFS endian helpers, UFS on-disk structures, cylinder helpers, inode operations, Linux fs-context/parser APIs, exportfs helpers, delayed work, slab caches, and VFS block-device mounting.

## Risks
A wrong `ufstype` can corrupt media; the code warns when defaulting to `old`. Mount correctness depends on exact flavor flags for directory entry format, UID format, clean-state format, cylinder-group layout, and UFS1/UFS2 address width. Error paths must release partially read superblock/cylinder resources. Delayed superblock sync must be canceled during unmount after internal writeback.
