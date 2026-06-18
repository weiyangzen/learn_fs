# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/common.h

Defines public/common Ext2Fsd IOCTL payloads, performance-statistics layouts, volume-property structures, and mount-point management structures.

Key contents:
- Global application IOCTLs: `IOCTL_APP_VOLUME_PROPERTY`, `IOCTL_APP_QUERY_PERFSTAT`, and `IOCTL_APP_MOUNT_POINT`.
- Performance-statistic slot IDs for IRP contexts, VCBs, FCBs, CCBs, MCBs, extents, read/write contexts, VPBs, names, directory entries, disk buffers, inodes, dentries, and buffer heads.
- `EXT2_STAT_ARRAY_V1` and `EXT2_STAT_ARRAY_V2` unions for named and indexed memory/stat counters.
- `EXT2_PERF_STATISTICS_V1` and `EXT2_PERF_STATISTICS_V2` layouts, including per-major-function processed/current IRP counts and allocation statistics.
- Volume-property command constants for querying/setting versions and property generations.
- `EXT2_VOLUME_PROPERTY`, `EXT2_VOLUME_PROPERTY2`, and `EXT2_VOLUME_PROPERTY3`, covering read-only/ext2/ext3 flags, codepage, UUID, drive letter, bitmap checks, hiding patterns, automount, and user/group IDs.
- `EXT2_VOLUME_PROPERTY_VERSION` for version/time/date reporting.
- `EXT2_QUERY_PERFSTAT` and size macros for V1/V2 perf-stat queries.
- `EXT2_MOUNT_POINT` plus add/delete DOS symlink commands for mount-point management.

Important invariants:
- Magic constants identify expected payload types: performance statistics, volume properties, and mount-point requests.
- V2 performance stats expand the slot array from `0x10` to `0x30` and add inode/name-entry/buffer-head counters.
- ReactOS uses `1ULL` for 64-bit `EXT2_VPROP3_*` flags; non-ReactOS uses MSVC-style `1ui64`.
- C++ builds model property generations through inheritance-like struct syntax, while C builds embed the previous structure as an anonymous field.

Filesystem relevance:
- This header defines the user/kernel control ABI for ReactOS ext2 volume properties, statistics, and drive-letter/mount-point operations.
- It is shared infrastructure for Ext2Fsd management tools and the kernel driver.

Notable risks:
- Several comments contain legacy typos, but the ABI field order and sizes are the important compatibility contract.
- Anonymous embedded struct usage and C++ inheritance-style declarations are compiler-sensitive.
