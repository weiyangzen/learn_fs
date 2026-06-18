# File Research: sources/local-fs/jfsutils/include/jfs_superblock.h

Defines the JFS aggregate superblock format.

Key contents:
- Defines `JFS_MAGIC` as `"JFS1"` and version `2`.
- Defines `LV_NAME_SIZE`.
- `struct superblock` includes magic/version, aggregate size/block geometry, AG size, flags/state, compression flag, secondary AIT/AIM PXDs, log device/serial/log extent, fsck workspace extent, update time, fsck log length/current half, legacy volume name, extendfs fields, volume UUID/label, and log UUID.

Interactions:
- Read and validated by `extract.c` and common superblock helpers.
- Uses `pxd_t` and `timestruc_t` from `jfs_types.h`; flags/states come from `jfs_filsys.h`.

Research notes:
- `s_fsckloglen` is total reserved fsck-log blocks divided among kept versions, which `extract.c` interprets as two halves.
