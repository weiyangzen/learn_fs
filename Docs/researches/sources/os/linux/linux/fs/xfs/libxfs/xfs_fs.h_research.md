# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_fs.h

## Purpose

`xfs_fs.h` defines the XFS userspace ABI: ioctl numbers, ioctl argument structures, geometry reports, bulk inode/stat interfaces, scrub/repair interfaces, parent pointer iteration, file range exchange operations, health monitoring, and media verification. It is LGPL-licensed and explicitly intended to compile under C++.

## Main Content

- Defines direct I/O and file extent mapping structures:
  - `struct dioattr`.
  - `struct getbmap`.
  - `struct getbmapx`.
  - BMAP input and output flags for attr fork, CoW fork, prealloc, delalloc, holes, shared extents.
- Defines fsmap owner constants for XFS metadata owners.
- Defines filesystem geometry structures:
  - Legacy V1 and V4 geometry.
  - Current `struct xfs_fsop_geom`, including health fields, realtime group fields, internal realtime start, and reserved blocks.
  - Geometry feature flags mirroring superblock feature state.
- Defines AG and realtime group geometry reporting:
  - `struct xfs_ag_geometry`.
  - `struct xfs_rtgroup_geometry`.
  - Sick/checked bit definitions for metadata health reporting.
- Defines bulk inode/stat and inode-number reporting:
  - Legacy `struct xfs_bstat`, `struct xfs_inogrp`, and `struct xfs_fsop_bulkreq`.
  - Current `struct xfs_bulkstat`, `struct xfs_inumbers`, request headers, and version constants.
  - Flags for AG-limited scans, special inode queries, 64-bit extent counts, and metadata directory visibility.
- Defines handle-based operations:
  - File handles, fsids, fids.
  - Path/fd/handle conversion request structures.
  - Attribute list/multiop by handle structures.
- Defines scrub and repair ABI:
  - `struct xfs_scrub_metadata`.
  - Scrub type IDs covering AG metadata, inode forks, directory/xattr/symlink, quotas, counters, parent pointers, metapaths, realtime group metadata.
  - Input/output scrub flags and vectored scrub structures.
- Defines atomic file data exchange ABI:
  - `struct xfs_exchange_range`.
  - `struct xfs_commit_range`.
  - Flags for to-EOF, dsync, dry-run, and file1-written-only exchange.
- Defines parent pointer iteration:
  - `struct xfs_getparents`.
  - `struct xfs_getparents_by_handle`.
  - Record iteration helpers over userspace buffers.
- Defines health monitor ABI:
  - Event domains for mount, fs, AG, inode, realtime group, devices, and file ranges.
  - Event types for monitor state, unmount, sick/corrupt/healthy, shutdown, media errors, buffered/direct I/O errors, and data loss.
  - Event payload structures and monitor configuration.
- Defines media verification ABI:
  - `struct xfs_verify_media`.
  - Device IDs for data/log/realtime devices.
- Defines XFS ioctl command numbers.

## Key Interfaces and Invariants

- This file is ABI-stable; structure padding, reserved fields, and explicit fixed-width types are part of compatibility.
- Many newer interfaces provide version fields and reserved space to allow extension without breaking userspace.
- Health fields in geometry and bulkstat mirror in-core sickness masks defined elsewhere, including `xfs_health.h`.
- Scrub type numbers and ioctl numbers are externally visible and must not be renumbered.
- Some legacy ioctls are preserved or aliased even when deprecated.

## Dependencies

This header references Linux UAPI concepts such as `FS_IOC_*`, `FMR_OWNER`, `__user`, fixed-width kernel integer types, and xattr list limits. It bridges XFS internal health/scrub concepts to userspace tools such as xfs_io, xfs_scrub, and administrative monitors.
