# File Research: sources/local-fs/xfsdump/common/fs.c

## Summary
Provides filesystem discovery helpers for xfsdump. It resolves a user-supplied source string into filesystem type, block device, mount point, and XFS UUID by reading the mounted-filesystem table and querying XFS geometry.

## Main Responsibilities
- Build an in-memory list from `setmntent(MOUNTED, "r")`.
- Resolve block-device paths directly or by matching `st_rdev`.
- Resolve mount-point paths by exact mount-table match.
- Fill output buffers for fs type, block device, mount point, and UUID.
- Query XFS UUID with `XFS_IOC_FSGEOMETRY_V1`.
- Estimate in-use inode count via `statvfs()`.

## Important Behavior
`fs_info()` first checks whether the user string is a block device. If so, it looks up the corresponding mount-table entry by block path or device number. Otherwise it treats the string as a mount point and looks that up directly.

If the mount-table entry lacks a type, `fs_info()` falls back to the caller-provided default type. On success it calls `fs_getid()` for the mount point and logs the UUID.

`fs_mounted()` is intentionally shallow: it returns true if the mount-point string is non-empty.

`fs_getid()` opens the mount point and issues `XFS_IOC_FSGEOMETRY_V1`; failures clear the UUID and return `-1`.

`fs_getinocnt()` returns `f_files - f_ffree` when `statvfs()` succeeds and the values are sane.

## Dependencies
Depends on mount table APIs, `stat64`, `statvfs`, Linux/XFS ioctl definitions, UUID APIs, and xfsdump logging/types.

## Risks
Mount-point lookup is exact-string only; it does not canonicalize paths or handle bind mounts beyond what appears in the mount table.

`fs_mounted()` does not verify live mount state or UUID/type consistency.

Output copying relies on `assert(strlen(...) < bufsz)` rather than runtime bounds handling, so production builds without assertions may not guard against unexpectedly long mount-table fields.

`fs_getid()` is XFS-specific; non-XFS sources will fail UUID lookup even if mount-table resolution succeeds.
