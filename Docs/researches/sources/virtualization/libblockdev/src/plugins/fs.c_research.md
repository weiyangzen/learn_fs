# File Research: sources/virtualization/libblockdev/src/plugins/fs.c

## Role

`fs.c` is the top-level filesystem plugin dispatcher. It initializes shared filesystem-plugin state and routes technology availability checks to per-filesystem modules.

## Initialization

`bd_fs_init()` calls `mnt_init_debug(0)` so libmount honors `LIBMOUNT_DEBUG`.

`bd_fs_close()` resets cached dependency availability for every per-filesystem implementation: ext, xfs, vfat, ntfs, exfat, btrfs, udf, f2fs, and nilfs.

## Technology Availability

`bd_fs_is_tech_avail()` treats generic and mount technologies as always available. For real filesystem technologies it validates the enum range, then dispatches to:

- `bd_fs_ext_is_tech_avail()`
- `bd_fs_xfs_is_tech_avail()`
- `bd_fs_vfat_is_tech_avail()`
- `bd_fs_ntfs_is_tech_avail()`
- `bd_fs_f2fs_is_tech_avail()`
- `bd_fs_nilfs2_is_tech_avail()`
- `bd_fs_exfat_is_tech_avail()`
- `bd_fs_btrfs_is_tech_avail()`
- `bd_fs_udf_is_tech_avail()`

## Dependencies

- libmount for debug initialization.
- libblockdev `check_deps` mechanism indirectly through per-filesystem modules.
- `fs/common.h` for dependency-cache reset declarations.

## Notable Risks

- Dispatch relies on `BD_FS_LAST_FS` matching the highest filesystem enum value in `fs.h`.
- Per-filesystem availability is spread across multiple compilation units, so adding a filesystem requires updates in the enum, dispatch, close reset, Makefile, and public includes.
