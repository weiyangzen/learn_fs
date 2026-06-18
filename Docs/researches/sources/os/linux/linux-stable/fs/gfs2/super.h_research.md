# File Research: sources/os/linux/linux-stable/fs/gfs2/super.h

## Scope

This header exposes GFS2 superblock, journal, statfs, freeze, filesystem type, export, dentry, super operation, and xattr handler interfaces.

## APIs And Definitions

- Supported on-disk format range is declared as `GFS2_FS_FORMAT_MIN` 1801 through `GFS2_FS_FORMAT_MAX` 1802.
- `gfs2_jindex_size()` safely returns `sd_journals` under `sd_jindex_spin`.
- Declarations cover journal descriptor lookup/check/free, master-dir lookup, read-write/read-only transitions, uevents/thread destruction, statfs initialization/change/sync, freeze work, local statfs inode helpers, and `free_sbd()`.
- External operation tables include `gfs2_fs_type`, `gfs2meta_fs_type`, `gfs2_export_ops`, `gfs2_super_ops`, and `gfs2_dops`.
- Xattr handler pointer arrays are exported for format-min/format-max handler selection.

## Dependencies

The header depends on Linux `fs.h`, `dcache.h`, and GFS2 in-core structures.

## Risks And Invariants

Format gating matters for xattr namespace support in `xattr.c`. `gfs2_jindex_size()` is only a snapshot; callers needing descriptor stability must still hold appropriate locks. Lifecycle routines declared here often assume system inodes and glocks have already been initialized by mount code outside this file group.
