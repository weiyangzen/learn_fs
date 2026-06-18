# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_fs.h

## Role in the repository

`xfs_fs.h` is the XFS userspace ABI header. It defines ioctl structures, ioctl numbers, geometry reports, bulk inode reporting, scrub and repair controls, file range exchange/commit operations, parent pointer iteration, health monitoring, media verification, and legacy compatibility interfaces. It is LGPL-licensed and written to remain C++ compilable.

## Mapping and extent reporting ABI

The file defines:
- `struct dioattr` for direct I/O alignment limits.
- `struct getbmap` and `struct getbmapx` for block mapping queries.
- `BMV_IF_*` input flags for data, attr, CoW, prealloc, delalloc, and hole filtering.
- `BMV_OF_*` output flags for preallocation, delayed allocation, last extent, and shared extents.
- `XFS_FMR_OWN_*` owner values for `FS_IOC_GETFSMAP`.

These structures provide userspace with file and filesystem extent layout information.

## Filesystem geometry and AG geometry

The header defines multiple geometry ABI versions:
- `xfs_fsop_geom_v1`
- `xfs_fsop_geom_v4`
- `xfs_fsop_geom`

The current geometry structure reports filesystem size, realtime size, log placement, UUID, stripe geometry, feature flags, health masks, realtime group count/size, internal realtime start, and zoned realtime reservations.

Feature flag exports include attr, nlink, quota, alignment, dirv2, logv2, sector size, attr2, projid32, lazy superblock counters, v5 superblock, ftype, FINOBT, sparse inodes, RMAPBT, reflink, bigtime, INOBT counters, 64-bit extent counters, exchange range, parent pointers, metadata directories, and zoned realtime.

`struct xfs_ag_geometry` reports per-AG length, free blocks, inode counts, health masks, and flags. `struct xfs_rtgroup_geometry` performs the same role for realtime groups and includes zoned write pointer reporting.

## Bulk inode and inode number ABI

Legacy `struct xfs_bstat` and newer `struct xfs_bulkstat` report inode attributes, timestamps, extent counts, project id, fork offset, CoW/extent hints, health state, and large data fork extent counts.

`struct xfs_inogrp` and `struct xfs_inumbers` report allocated inode chunks. `struct xfs_bulk_ireq` is the shared request header for modern bulkstat and inumbers ioctls, with flags for AG-limited scans, special inode requests, 64-bit extent count reporting, and metadata directory visibility.

## Handles and attribute-by-handle ABI

The file defines handle request structures for path-to-handle, fd-to-handle, open-by-handle, readlink-by-handle, attr-list-by-handle, and attr-multi-by-handle. Attribute list structures mirror libattr ABI layouts, including the opaque attrlist cursor and variable-length name entries.

## Scrub and repair ABI

`struct xfs_scrub_metadata` describes one scrub target. `XFS_SCRUB_TYPE_*` enumerates scrub targets for superblocks, AG headers, btrees, inode forks, directories, xattrs, symlinks, parent pointers, realtime metadata, quotas, fs counters, link counts, directory tree structure, metadata paths, realtime group superblocks, realtime rmap, and realtime refcount.

Scrub flags distinguish requested repair or forced rebuild from output states such as corrupt, preen, cross-reference failure, cross-reference corruption, incomplete, warning, and no repair needed. The vectored scrub ABI uses `struct xfs_scrub_vec` and `struct xfs_scrub_vec_head`, with a barrier vector type for dependency-sensitive batches.

## File exchange, commit range, and parent pointers

`struct xfs_exchange_range` describes an atomic range exchange between file1 and file2. `struct xfs_commit_range` extends this with file2 freshness fields so a prepared file can be committed only if the target has not changed.

Exchange flags support exchange-to-EOF, dsync, dry run, and file1-written-only behavior.

Parent pointer iteration uses `struct xfs_getparents`, `struct xfs_getparents_rec`, and by-handle variants. Inline helpers advance through variable-length parent records safely within the supplied buffer.

## Health monitor and media verification ABI

The health monitor section defines event domains for mount, fs, AG, inode, realtime group, devices, and file ranges. Event types include monitor status, unmount, sick/corrupt/healthy metadata, shutdown, media errors, pagecache I/O errors, direct I/O errors, and data loss.

`struct xfs_health_monitor_event` carries a timestamp and a domain-specific payload. `struct xfs_health_monitor` starts monitoring, and `struct xfs_health_file_on_monitored_fs` validates that an fd belongs to the monitored filesystem.

`struct xfs_verify_media` defines device media verification ranges and pacing, with optional reporting.

## Ioctl command surface

The bottom of the file assigns the XFS ioctl numbers for direct I/O info, extent maps, reserve/unreserve/zero range, EOF block trimming, scrub, AG geometry, parent pointers, vectored scrub, realtime group geometry, health monitor, media verify, geometry, bulkstat, inumbers, handles, growfs, counts, reserved blocks, error injection, freeze/thaw, going down, exchange range, and commit range.

## Important invariants

- This header is userspace ABI; structure sizes, field offsets, reserved zero fields, and ioctl numbers are compatibility-sensitive.
- Legacy and modern structures coexist because old tools and kernels still consume old ABI layouts.
- Health masks in this file are exported encodings derived from internal health flags, not the internal flags themselves.
- Variable-length ABI buffers carry explicit sizes and record lengths; callers must not infer layout beyond the documented fields.
