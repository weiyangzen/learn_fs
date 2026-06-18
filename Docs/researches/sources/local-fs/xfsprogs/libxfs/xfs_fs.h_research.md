# File Research: sources/local-fs/xfsprogs/libxfs/xfs_fs.h

## Purpose
Defines the userspace-facing XFS filesystem ABI: ioctl numbers, ioctl payload structures, geometry records, bulkstat/inumbers records, scrub interfaces, health monitor events, media verification, parent-pointer iteration, exchange/commit range interfaces, and legacy compatibility structures.

## Main Contents
- Mapping and direct I/O:
  - `struct dioattr` for direct I/O alignment.
  - `struct getbmap` and `struct getbmapx` plus `BMV_IF_*` and `BMV_OF_*` flags for extent mapping queries.
  - FS map owner constants for XFS metadata classes.
- Filesystem geometry:
  - Versioned geometry structs `xfs_fsop_geom_v1`, `xfs_fsop_geom_v4`, and current `xfs_fsop_geom`.
  - Current geometry includes health bitmaps, realtime group count/size, internal realtime start, and zoned RT reservations.
  - Geometry feature flags mirror superblock features and are exported through `XFS_IOC_FSGEOMETRY`.
- AG and RT group geometry:
  - `struct xfs_ag_geometry` reports AG free blocks, inode counts, and health status.
  - `struct xfs_rtgroup_geometry` reports realtime group length and health status.
- Bulk inode reporting:
  - Legacy `xfs_bstat` and modern `xfs_bulkstat`.
  - `xfs_inogrp` and modern `xfs_inumbers`.
  - `xfs_bulk_ireq` controls bulkstat/inumbers requests with flags for AG restriction, special inode targets, 64-bit extent counts, and metadata directory visibility.
- Handles and attributes:
  - File handle structs and handle-based path/open/readlink/attribute ioctl payloads.
  - Attribute list cursor and multi-operation records matching libattr layouts.
- Scrub and repair:
  - `struct xfs_scrub_metadata` and scrub type constants for all major metadata classes.
  - Vectored scrub via `xfs_scrub_vec` and `xfs_scrub_vec_head`.
  - Scrub flags distinguish requested repair/rebuild from output conditions such as corrupt, preen, xfail, xcorrupt, incomplete, warning, and no-repair-needed.
  - Metadata path scrub selectors cover quota and realtime metadata directory entries.
- Exchange/commit range:
  - `struct xfs_exchange_range` and `struct xfs_commit_range` support crash-restartable file range exchange/commit workflows.
  - Flags cover to-EOF exchange, dsync, dry run, and file1-written-only exchanges.
- Parent pointers:
  - `xfs_getparents`, `xfs_getparents_rec`, by-handle variant, cursor helpers, and flags for root/done reporting.
- Health monitor and media verification:
  - Defines health monitor domains, event types, event payload union, monitor control struct, and same-filesystem fd check.
  - Defines shutdown reason bits, media error payloads, file range I/O event payloads, and `xfs_verify_media`.
- Ioctl numbers:
  - Maps all XFS ioctl commands, including legacy IRIX-derived commands and current Linux commands, under the `'X'` ioctl namespace.
  - Keeps basic block macros available when not supplied by the build environment.

## Dependencies and Integration
- Included by userspace tools and libxfs code that must share ioctl ABI with Linux XFS.
- Depends on kernel-style integer and ioctl types, `FS_IOC_*`, `FMR_OWNER`, user pointer annotations, and basic XFS typedefs supplied elsewhere.
- Health flags correspond to sickness masks defined in `xfs_health.h`.
- Geometry flags correspond to superblock feature bits in `xfs_format.h`.

## Invariants and Constraints
- The file explicitly states it must compile with C++ compilers.
- Struct layout, padding, reserved fields, and ioctl numbers are ABI-stable and must not be casually changed.
- Reserved fields are generally required to be zero, enabling future ABI expansion.
- Legacy and modern versions coexist because older tools and kernels still use older structure layouts.
- `XFS_BULK_IREQ_NREXT64` changes where extent count is returned and defines overflow behavior.

## Notable Risks
- ABI breakage is the main risk: changing type widths, field order, padding, or ioctl numbers can break userspace.
- Several features represented here are coupled to other files: adding a scrub type or health bit requires conversion code in health, scrub, geometry, and reporting paths.
- Health monitor unions are deliberately non-anonymous for bindgen compatibility; changing that could break Rust/Python client generation.
