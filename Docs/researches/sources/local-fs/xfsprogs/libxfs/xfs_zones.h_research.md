# File Research: sources/local-fs/xfsprogs/libxfs/xfs_zones.h

This header defines zoned realtime reservation constants and declares block-zone validation.

`XFS_GC_ZONES` reserves three zones for garbage collection progress: one move target, one spare relocation zone, plus slack for simpler accounting. `XFS_RESERVED_ZONES` and `XFS_MIN_ZONES` add user-write requirements. `XFS_OPEN_GC_ZONES` and `XFS_MIN_OPEN_ZONES` reserve open-zone capacity for GC even when writers are waiting. `XFS_DEFAULT_MAX_OPEN_ZONES` defaults to 128 for devices without explicit open-zone limits or regular devices using the zoned allocator.

`xfs_validate_blk_zone` is declared with expected raw zone size, expected usable capacity, and a returned write pointer. It is implemented in `xfs_zones.c` and depends on mount block conversion geometry.
