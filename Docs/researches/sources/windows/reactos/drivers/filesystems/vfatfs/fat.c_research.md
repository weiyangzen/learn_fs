# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/fat.c

Purpose: Implements File Allocation Table access, cluster allocation/free accounting, dirty-bit handling, and FAT32 FSINFO free-cluster updates.

Key routines:
- `FAT12GetNextCluster`, `FAT16GetNextCluster`, and `FAT32GetNextCluster` read the next cluster from the cached FAT file object, normalize end-of-chain values to `0xffffffff`, and detect zero/corrupt entries in FAT16/32 paths.
- `FAT12FindAndMarkAvailableCluster`, `FAT16FindAndMarkAvailableCluster`, and `FAT32FindAndMarkAvailableCluster` scan from `LastAvailableCluster`, wrap once to cluster 2, mark the found cluster EOF, and decrement cached free-cluster counts when valid.
- `FAT12CountAvailableClusters`, `FAT16CountAvailableClusters`, `FAT32CountAvailableClusters`, and `CountAvailableClusters` compute and cache free-cluster counts under `FatResource`.
- `FAT12WriteCluster`, `FAT16WriteCluster`, `FAT32WriteCluster`, and `WriteCluster` mutate FAT entries and update free-cluster accounting based on old/new values.
- `ClusterToSector` maps data cluster numbers to sectors.
- `GetNextCluster` and `GetNextClusterExtend` wrap FAT-specific get/extend operations with resource locking.
- `GetDirtyStatus`, `SetDirtyStatus`, `FAT16GetDirtyStatus`, `FAT32GetDirtyStatus`, `FAT16SetDirtyStatus`, and `FAT32SetDirtyStatus` read/write FAT16/FAT32 volume dirty bits in boot-sector reserved fields.
- `FAT32UpdateFreeClustersCount` writes the cached free-cluster count into the FAT32 FSINFO sector.

Implementation notes:
- `CACHEPAGESIZE` uses at least one page and may use a whole cluster when clusters exceed page size.
- FAT12 code maps/pins the full FAT because 12-bit entries can cross byte boundaries; FAT16/FAT32 operate in chunks.
- FAT32 preserves the high 4 reserved bits when writing cluster entries.
- Dirty-bit operations can optionally bypass cache manager via `VOLUME_IS_NOT_CACHED_WORK_AROUND_IT`, but the normal path pins the volume FCB cache.

Dependencies and interactions:
- Used by allocation-size changes, directory creation/deletion, move/delete cleanup, offset-to-cluster traversal, and volume metadata reporting.
- Protected by `DeviceExt->FatResource` wrappers for shared/exclusive access.

Notable limitations and risks:
- FAT12 `GetNextCluster` asserts on zero but does not mirror the FAT16/32 `STATUS_FILE_CORRUPT_ERROR` handling.
- Some callers ignore `WriteCluster` status, so FAT-chain mutation failures can be underreported in higher-level operations.
