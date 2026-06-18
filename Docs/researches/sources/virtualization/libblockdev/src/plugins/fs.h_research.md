# File Research: sources/virtualization/libblockdev/src/plugins/fs.h

## Role

`fs.h` is the umbrella public header for libblockdev's filesystem plugin.

## Public Error and Technology Model

It declares `BDFSError`, with errors for unavailable tech, invalid inputs, parse failures, generic failures, missing filesystem, pipe errors, unmount failure, unsupported operation, not mounted, authorization, invalid label/UUID, and unknown filesystem.

`BDFSTech` identifies generic operations, mount operations, and supported filesystems: ext2/3/4, XFS, VFAT, NTFS, F2FS, NILFS2, exFAT, Btrfs, and UDF.

`BDFSTechMode` exposes operation classes: mkfs, wipe, check, repair, set label, query, resize, and set UUID.

## Public API

The top-level functions are lifecycle and availability:

- `bd_fs_init()`
- `bd_fs_close()`
- `bd_fs_is_tech_avail()`

The header then includes every per-filesystem and generic/mount subheader, making this the main consumer include for filesystem operations.

## Notable Risks

The `BD_FS_OFFSET`, `BD_FS_LAST_FS`, and `BD_FS_MODE_LAST` macros must remain synchronized with enum contents and per-filesystem dispatch arrays.
